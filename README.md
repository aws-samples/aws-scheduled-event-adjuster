# aws-scheduled-scaling-adjuster

Amazon EC2 Auto Scaling allows modifying the size of an instance fleet depending on the time of the day. However, the scaling schedule is always set in Coordinated Universal Time (UTC). As some countries throughout the world implement Daylight Saving Time, these schedules need to be updated twice per year to account for the changes in the offset between local times and UTC.

This solution aims to automatically perform these adjustments, without human intervention, while remaining flexible, configurable, and inexpensive.

## Solution architecture

The solution is built on top of serverless components, following an event-driven architecture.

![](architecture_diagram.png)

## Deploying the solution

This project is built using the AWS Serverless Application Model (SAM), a framework extending AWS CloudFormation syntax to easily define serverless components such as AWS Lambda functions or Amazon DynamoDB tables.

The following tools are required to deploy it:

* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3](https://www.python.org/downloads/)
* [Docker](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts. If you choose to save your choices to `samconfig.toml`, then you no longer will need to pass the `--guided` flag, as the SAM CLI will read your settings from it.

**Note:** You will be asked for an email address: this is where notifications will be sent whenever the solution performs changes to any of your Auto Scaling Groups. The email you enter will not be used for any other purpose.

## How to use

All changes are done by the scheduler adjuster function. This function is triggered twice per day by an Amazon EventBridge scheduled event.

The solution is opt-in: the adjuster queries all Auto Scaling Groups (ASG) in its AWS account, but only takes action on those which have been tagged specifically; otherwise they are ignored. For an ASG to be processed, it needs to have the following tags:

* `scheduled-scaling-adjuster:enabled`: this tag tells the adjuster to process this ASG. The value of this tag is ignored - only its presence is enough for the adjuster to process the ASG.
* `scheduled-scaling-adjuster:local-timezone`: this tag tells the adjuster in which timezone the schedules are defined. The value must be a valid timezone name, such as `America/New_York` or `Europe/Lisbon`.

Additionally, for each scheduled scaling policy that needs to be controlled by the solution, an additional tag needs to be present:

* `scheduled-scaling-aduster:local-time:<ACTION_NAME>`: this tag tells the adjuster the time (at the local timezone) the action needs to occur. If the action name is _MorningScaleOut_, then the tag key must be `scheduled-scaling-aduster:local-time:MorningScaleOut`.

### Example

We have one ASG with two scaling policies. One, named _MorningScaleOut_, must trigger at 08:00, whereas the other one, _EveningScaleIn_, must happen at 20:00. The specified times are local to the city of Madrid, Spain.

Thus, the ASG must be tagged accordingly:

* `scheduled-scaling-adjuster:enabled` = (no value)
* `scheduled-scaling-adjuster:local-timezone` = `Europe/Madrid`
* `scheduled-scaling-adjuster:local-time:MorningScaleOut` = `08:00`
* `scheduled-scaling-adjuster:local-time:EveningScaleIn` = `20:00`

## Roadmap

All changes done by the solution are logged into Amazon CloudWatch, but we're currently working on an audit mechanism that will allow operators to easily query changes done to a specific Auto Scaling Group and date.

## Developing

Dependencies for the `AdjustSchedule` function are defined in `adjust_schedule_function/requirements.txt`. To test the function locally, you can build with the following command:

```bash
sam build --use-container
```

The function can be locally invoked using `sam local invoke`. The `events` directory contains test events that can be passed on the function invocation.

```bash
sam local invoke HelloWorldFunction --event events/event.json
```

### Unit tests

Tests are defined in the `tests` folder in this project, and can be run using the [pytest](https://docs.pytest.org/en/latest/):

```bash
scheduled-scaling-adjuster$ pip install pytest pytest-mock --user
scheduled-scaling-adjuster$ python -m pytest tests/ -v
```
