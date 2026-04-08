import json
import boto3
from datetime import datetime

s3 = boto3.client("s3")

def read_file(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        print("Read file: " + key)
        return content
    except Exception as e:
        print("Read failed: " + str(e))
        return None

def process_content(content, filename):
    try:
        lines = content.split("\n")
        words = content.split()
        chars = len(content)
        non_empty = [l for l in lines if l.strip()]
        longest = max(lines, key=len) if lines else ""
        report = {
            "filename": filename,
            "processed_at": str(datetime.now()),
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty),
            "total_words": len(words),
            "total_chars": chars,
            "longest_line": longest.strip(),
            "first_line": lines[0].strip() if lines else "",
            "status": "processed successfully"
        }
        print("Processed: " + filename)
        return report
    except Exception as e:
        print("Process failed: " + str(e))
        return None

def save_result(bucket, result, original_key):
    try:
        base_name = original_key.split("/")[-1]
        result_key = "results/" + base_name.replace(".txt", "_result.json")
        s3.put_object(Bucket=bucket, Key=result_key, Body=json.dumps(result, indent=4).encode("utf-8"), ContentType="application/json")
        print("Saved result: " + result_key)
        return result_key
    except Exception as e:
        print("Save failed: " + str(e))
        return None

def lambda_handler(event, context):
    try:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        print("New file: " + key)
        content = read_file(bucket, key)
        if content is None:
            return {"statusCode": 400, "body": "Failed to read file"}
        result = process_content(content, key)
        if result is None:
            return {"statusCode": 400, "body": "Failed to process file"}
        result_key = save_result(bucket, result, key)
        return {"statusCode": 200, "body": json.dumps({"message": "File processed successfully", "input_file": key, "result_file": result_key, "summary": result})}
    except Exception as e:
        print("Lambda failed: " + str(e))
        return {"statusCode": 500, "body": "Error: " + str(e)}
