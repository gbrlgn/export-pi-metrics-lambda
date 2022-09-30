import time
import boto3

pi_client = boto3.client('pi')
rds_client = boto3.client('rds')
cw_client = boto3.client('cloudwatch')

engine_metrics = {
    'postgres': [
        'db.Cache.blks_hit',
        'db.Cache.buffers_alloc',
        'db.Checkpoint.buffers_checkpoint',
        'db.Checkpoint.checkpoint_sync_time',
        'db.Checkpoint.checkpoint_write_time',
        'db.Checkpoint.checkpoints_req',
        'db.Checkpoint.checkpoints_timed',
        'db.Checkpoint.maxwritten_clean',
        'db.Concurrency.deadlocks',
        'db.IO.blk_read_time',
        'db.IO.blks_read',
        'db.IO.buffers_backend',
        'db.IO.buffers_backend_fsync',
        'db.IO.buffers_clean',
        'db.SQL.tup_deleted',
        'db.SQL.tup_fetched',
        'db.SQL.tup_inserted',
        'db.SQL.tup_returned',
        'db.SQL.tup_updated',
        'db.Temp.temp_bytes',
        'db.Temp.temp_files',
        'db.Transactions.active_transactions',
        'db.Transactions.blocked_transactions',
        'db.Transactions.max_used_xact_ids',
        'db.Transactions.xact_commit',
        'db.Transactions.xact_rollback',
        'db.User.numbackends',
        'db.WAL.archived_count',
        'db.WAL.archive_failed_count'
    ],
    'mysql': [
        'db.SQL.Com_analyze',
        'db.SQL.Com_optimize',
        'db.SQL.Com_select',
        'db.Users.Connections',
        'db.SQL.Innodb_rows_deleted',
        'db.SQL.Innodb_rows_inserted',
        'db.SQL.Innodb_rows_read',
        'db.SQL.Innodb_rows_updated',
        'db.SQL.Select_full_join',
        'db.SQL.Select_full_range_join',
        'db.SQL.Select_range',
        'db.SQL.Select_range_check',
        'db.SQL.Select_scan',
        'db.SQL.Slow_queries',
        'db.SQL.Sort_merge_passes',
        'db.SQL.Sort_range',
        'db.SQL.Sort_rows',
        'db.SQL.Sort_scan',
        'db.SQL.Questions',
        'db.Locks.Innodb_row_lock_time',
        'db.Locks.Table_locks_immediate',
        'db.Locks.Table_locks_waited',
        'db.Users.Aborted_clients',
        'db.Users.Aborted_connects',
        'db.Users.Threads_created',
        'db.Users.Threads_running',
        'db.IO.Innodb_data_writes',
        'db.IO.Innodb_dblwr_writes',
        'db.IO.Innodb_log_write_requests',
        'db.IO.Innodb_log_writes',
        'db.IO.Innodb_pages_written',
        'db.Temp.Created_tmp_disk_tables',
        'db.Temp.Created_tmp_tables',
        'db.Cache.Innodb_buffer_pool_pages_data',
        'db.Cache.Innodb_buffer_pool_pages_total',
        'db.Cache.Innodb_buffer_pool_read_requests',
        'db.Cache.Innodb_buffer_pool_reads',
        'db.Cache.Opened_tables',
        'db.Cache.Opened_table_definitions',
        'db.Cache.Qcache_hits'
    ]
}


def lambda_handler(event, context):
    pi_instances = get_pi_instances()

    for instance in pi_instances:
        pi_response = get_resource_metrics(instance)
        if pi_response:
            send_cloudwatch_data(pi_response)

    return {
        'statusCode': 200,
        'body': 'ok'
    }


def get_pi_instances():
    response = rds_client.describe_db_instances()

    return filter(
        lambda _: _.get('PerformanceInsightsEnabled', False),   
        response['DBInstances']
    )


def get_resource_metrics(instance):
    metric_queries = []
    if engine_metrics.get(instance['Engine'], False):
        for metric in engine_metrics[instance['Engine']]:
            metric_queries.append({'Metric': metric})

    if not metric_queries:
        return

    return pi_client.get_resource_metrics(
        ServiceType='RDS',
        Identifier=instance['DbiResourceId'],
        StartTime=time.time() - 300,
        EndTime=time.time(),
        PeriodInSeconds=60,
        MetricQueries=metric_queries
    )

def send_cloudwatch_data(pi_response):
    metric_data = []

    for metric_response in pi_response['MetricList']:
        cur_key = metric_response['Key']['Metric']

        for datapoint in metric_response['DataPoints']:
            value = datapoint.get('Value', None)

            if value:
                metric_data.append({
                    'MetricName': cur_key,
                    'Dimensions': [
                        {
                            'Name':'DbiResourceId',    
                            'Value':pi_response['Identifier']
                        } 
                    ],
                    'Timestamp': datapoint['Timestamp'],
                    'Value': datapoint['Value']
                })

    if metric_data:
        cw_client.put_metric_data(
            Namespace='ExportPILambda',
            MetricData= metric_data
        )