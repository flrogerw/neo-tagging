import boto3

FILE_NAME = 'transcript.txt'
EXCLUDED_FILE_NAME = 'delineated_transcript.txt'


class TagS3:

    def __init__(self, bucket):
        self.bucket = bucket
        self.s3 = boto3.client('s3')

    def get_latests(self):
        try:
            all_files = []
            # Initial Boto3 command to list objects and filter by the file name
            paginator = self.s3.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.bucket)

            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if FILE_NAME in obj['Key'] and EXCLUDED_FILE_NAME not in obj['Key']:
                            all_files.append({'Key': obj['Key'], 'LastModified': obj['LastModified']})
            # Get the newest 1000 files
            return sorted(all_files, key=lambda x: x['LastModified'], reverse=True)[:100]
        except Exception as err:
            print(err)
    def get_content(self, file):
        # Retrieve the contents of each file and pass them to another function
        obj = self.s3.get_object(Bucket=self.bucket, Key=file['Key'])
        file_contents = obj['Body'].read().decode('utf-8')
        return file_contents
