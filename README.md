# Notes

Project for learning to use Python with AWS-CDK and constructs such as Lambda, DynamoDB and ApiGateway

The contstruct includes a lambda layer which does not appear in github, this is because it is a directory full of python packages. AWS Lambda layer only accepts the path python/ and python/lib/python3.8/site-packages (note python3.8 in file path should be the same for both your system and the lambda) for the lambda function to access. I would have liked to just have a requirements.txt file which can be installed if the repo is forked - but the path becomes different when installing from a virtual environment. It also becomes too large to upload. 

To create the packages for the layer, which the construct accepts, run these commands (inside the root of the project folder):

```
mkdir -p layer/python/lib/python3.8/site-packages/
pip install --target=layer/python/lib/python3.8/site-packages/ pandas
``` 

There are other ways to access and install external modules in lambda, such as with bundling a docker image with scripts in the AWS CDK construct or using the expiremental PythonFunction construct. However,the installation scripts in that image and PythonFunction run whenever "cdk deploy --hotswap" is initiated (to change some code in the lambda function), even though no resources in the stack were manipulated.



# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
