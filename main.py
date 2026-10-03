import boto3
import json

from s3_upload import upload_inventory


# -----------------------------
# AWS Session
# -----------------------------
session = boto3.Session(profile_name="aws-project")

ec2 = session.client("ec2")
sts = session.client("sts")


# -----------------------------
# Verify AWS Connection
# -----------------------------
identity = sts.get_caller_identity()

print("AWS Account:", identity["Account"])
print("AWS Region:", session.region_name)


# -----------------------------
# Get EC2 Instances
# -----------------------------
response = ec2.describe_instances()

inventory = []


# -----------------------------
# Check for EC2 Instances
# -----------------------------
if not response["Reservations"]:
    print("No EC2 instances found.")

else:

    print("\nEC2 Inventory")
    print("=" * 50)

    for reservation in response["Reservations"]:

        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            instance_type = instance["InstanceType"]
            availability_zone = instance["Placement"]["AvailabilityZone"]
            private_ip = instance.get("PrivateIpAddress")

            # -----------------------------
            # Read EC2 Tags
            # -----------------------------
            name = "N/A"
            environment = "N/A"
            auto_start = "N/A"

            for tag in instance.get("Tags", []):

                if tag["Key"] == "Name":
                    name = tag["Value"]

                elif tag["Key"] == "Environment":
                    environment = tag["Value"]

                elif tag["Key"] == "AutoStart":
                    auto_start = tag["Value"]


            # -----------------------------
            # EC2 Auto-Start Automation
            # -----------------------------
            if (
                state == "stopped"
                and environment == "Dev"
                and auto_start == "True"
            ):

                print(f"\nStarting EC2 instance: {instance_id}")
                print(f"Name: {name}")
                print(f"Environment: {environment}")
                print(f"AutoStart: {auto_start}")

                ec2.start_instances(
                    InstanceIds=[instance_id]
                )

                print("Waiting for instance to reach running state...")

                waiter = ec2.get_waiter("instance_running")

                waiter.wait(
                    InstanceIds=[instance_id]
                )

                print(f"Instance {instance_id} is now running.")

                # Update state after starting
                state = "running"


            # -----------------------------
            # Create Inventory Record
            # -----------------------------
            instance_data = {
                "instance_id": instance_id,
                "state": state,
                "instance_type": instance_type,
                "availability_zone": availability_zone,
                "private_ip": private_ip,
                "name": name,
                "environment": environment,
                "auto_start": auto_start
            }

            inventory.append(instance_data)


            # -----------------------------
            # Display Inventory
            # -----------------------------
            print(f"Instance ID: {instance_id}")
            print(f"State: {state}")
            print(f"Instance Type: {instance_type}")
            print(f"Availability Zone: {availability_zone}")
            print(f"Private IP: {private_ip}")
            print(f"Name: {name}")
            print(f"Environment: {environment}")
            print(f"AutoStart: {auto_start}")
            print("-" * 50)


# -----------------------------
# Save Inventory as JSON
# -----------------------------
with open("inventory.json", "w") as file:

    json.dump(
        inventory,
        file,
        indent=4
    )

print("\nInventory saved to inventory.json")


# -----------------------------
# Upload Inventory to S3
# -----------------------------
upload_inventory()