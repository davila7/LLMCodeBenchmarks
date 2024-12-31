/**
 * Import the AWS SDK and configure AWS credentials.
 */
const AWS = require('aws-sdk');

/**
 * Configure AWS credentials using environment variables for security.
 */
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION
});

/**
 * Create S3 and EC2 client instances.
 */
const s3 = new AWS.S3();
const ec2 = new AWS.EC2();

/**
 * Define a function to create an S3 bucket.
 * @param {string} bucketName - The name of the bucket to create.
 * @param {string} region - The AWS region where the bucket will be created.
 */
const createS3Bucket = async (bucketName, region) => {
  try {
    const createBucketParams = {
      Bucket: bucketName,
      CreateBucketConfiguration: {
        LocationConstraint: region
      }
    };

    const data = await s3.createBucket(createBucketParams).promise();
    console.log(`Bucket created successfully: ${data.Location}`);
  } catch (err) {
    console.error(`Error creating bucket: ${err}`);
  }
};

/**
 * Define a function to launch an EC2 instance.
 * @param {string} imageId - The AMI ID for the instance.
 * @param {string} instanceType - The type of EC2 instance.
 * @param {string} keyName - The name of the key pair for SSH access.
 */
const launchEC2Instance = async (imageId, instanceType, keyName) => {
  try {
    const params = {
      ImageId: imageId,
      InstanceType: instanceType,
      KeyName: keyName,
      MinCount: 1,
      MaxCount: 1
    };

    const data = await ec2.runInstances(params).promise();
    console.log(`Instance launched successfully: ${data.Instances[0].InstanceId}`);
    return data.Instances[0].InstanceId;
  } catch (err) {
    console.error(`Error launching EC2 instance: ${err}`);
  }
};

/**
 * Example usage of the functions.
 */
const bucketName = 'your-bucket-name';
const region = 'your-aws-region';
createS3Bucket(bucketName, region);

const imageId = 'ami-0c55b159cbfafe1f0';  // Example AMI ID
const instanceType = 't2.micro';
const keyName = 'your-key-pair-name';
launchEC2Instance(imageId, instanceType, keyName);
