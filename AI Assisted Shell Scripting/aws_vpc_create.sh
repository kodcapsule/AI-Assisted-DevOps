#!/bin/bash

# Description: This script creates a VPC in AWS
# - Create vpc
# - Create a public subnets
# - Create a private subnet
# - Create an internet gateway
# - Attach the internet gateway to the VPC
# - Create a route table
# - Create a route in the route table that points all traffic (
# - Verify if AWS CLI is installed . Confrim the OS and ask user to install AWS CLI . Check for  user OS  Windows,  MacOs or Linux.  Put all the code in a function and call the function
# - add two input arguments , create and delete to the script
# - Add a function to delete all the resources created by the script
# - Add a function to create all the resources created by the script
# - Add a function to display the usage of the script
# - Add a function to display the help of the script

 
#variables
VPC_CIDR_BLOCK="10.0.0.0/16"
VPC_CIDR_BLOCK="10.0.0.0/16"
PUBLIC_SUBNET_CIDR_BLOCK="10.0.3.0/24"
PRIVATE_SUBNET_CIDR_BLOCK="10.0.2.0/24"
VPC_NAME="my_vpc"   
PUBLIC_SUBNET_NAME="my_public_subnet"
PRIVATE_SUBNET_NAME="my_private_subnet"
INTERNET_GATEWAY_NAME="my_igw"
ROUTE_TABLE_NAME="my_route_table"
ROUTE_TABLE_ASSOCIATION_NAME="my_route_table_association"





verify_aws_cli() {
  if ! [ -x "$(command -v aws)" ]; then
    echo 'Error: AWS CLI is not installed.' >&2
    exit 1
  fi  
}




 




# Create VPC
create_vpc() {
  VPC_ID=$(aws ec2 create-vpc --cidr-block $VPC_CIDR_BLOCK --query 'Vpc.VpcId' --output text --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$VPC_NAME}]")
  echo "VPC created successfully with VPC ID: $VPC_ID"
}

# Create a public subnet
create_public_subnet() {
  PUBLIC_SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PUBLIC_SUBNET_CIDR_BLOCK --availability-zone us-east-1a --query 'Subnet.SubnetId' --output text --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PUBLIC_SUBNET_NAME}]")
  echo "Public subnet created successfully with Subnet ID: $PUBLIC_SUBNET_ID"
}

# Create a private subnet
create_private_subnet() {
  PRIVATE_SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_SUBNET_CIDR_BLOCK --availability-zone us-east-1a --query 'Subnet.SubnetId' --output text --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PRIVATE_SUBNET_NAME}]")
  echo "Private subnet created successfully with Subnet ID: $PRIVATE_SUBNET_ID"
}

# Create an internet gateway
create_internet_gateway() {
  INTERNET_GATEWAY_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$INTERNET_GATEWAY_NAME}]")
  echo "Internet gateway created successfully with Internet Gateway ID: $INTERNET_GATEWAY_ID"
}   

# Attach the internet gateway to the VPC 
attach_internet_gateway() {
  aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $INTERNET_GATEWAY_ID
  echo "Internet gateway attached to the VPC successfully"
}

# Create a route table
create_route_table() {
  ROUTE_TABLE_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$ROUTE_TABLE_NAME}]")
  echo "Route table created successfully with Route Table ID: $ROUTE_TABLE_ID"
}

# Create a route in the route table that points all traffic (
create_route() {
  aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block
  echo "Route created successfully in the route table"
}

# Associate the route table with the public subnet
associate_route_table() {
  aws ec2 associate-route-table --route-table-id $ROUTE_TABLE_ID --subnet-id $PUBLIC_SUBNET_ID --query 'AssociationId' --output text --tag-specifications "ResourceType=route-table-association,Tags=[{Key=Name,Value=$ROUTE_TABLE_ASSOCIATION_NAME}]"
  echo "Route table associated with the public subnet successfully"
}   

# Delete all the resources created by the script    
delete_resources() {
  echo " Deleting  resources created by the script"
  aws ec2 disassociate-route-table --association-id $ROUTE_TABLE_ASSOCIATION_NAME
  aws ec2 delete-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block
  aws ec2 delete-route-table --route-table-id $ROUTE_TABLE_ID
  aws ec2 detach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $INTERNET_GATEWAY_ID
  aws ec2 delete-internet-gateway --internet-gateway-id $INTERNET_GATEWAY_ID
  aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_ID
  aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_ID
  aws ec2 delete-vpc --vpc-id $VPC_ID
    echo "All resources deleted successfully"
}   

# Display the usage of the script

verify_aws_cli

display_usage() {
echo "This script requres at least one argument"
echo "for help on how to use the script run the script with help argument"
  echo "Usage: $0 [create | delete | help]"
}   

# Display the help of the script
display_help() {
  echo "This script creates a VPC and public subnets in AWS"
  echo "<OPTIONS:>"
  echo "$0 create: Creates a VPC , public subnet, private subnet, internet gateway, route table and route"
  echo "$0 delete: Deletes a VPC , public subnet, private subnet, internet gateway, route table and route"
  echo "$0 help: Displays the help"
}

# Check the number of arguments
if [ $# -ne 1 ]; then
  display_usage
  exit 1
fi

# Check the argument
case $1 in
  create)
    create_vpc
    create_public_subnet
    create_private_subnet
    create_internet_gateway
    attach_internet_gateway
    create_route_table
    create_route
    associate_route_table
    ;;
  delete)
    delete_resources
    ;;
  help)
    display_help
    exit 1
    ;;
    *)
    display_usage
    exit 1
    ;;

esac



