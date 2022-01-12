# Sonarqube Prometheus Exporter

Project to collect some Sonarqube metrics through the API and then expose such information for Prometheus collection.

With the intention of using Sonarqube for a range of projects, being able to increase or decrease the number of projects and directly their metrics, the project construction was thinking of several realities and not being directly linked to some metrics.

Importantly, Prometheus does not understand non-numeric values, so be aware if you want to add metrics that can return non-numeric values.

### Data flow diagram
![picture](https://github.com/afernandezrios90/sonarqube-prometheus-exporter/blob/master/images/Diagram.png)

### Main features

The exporter allows to gather the following metrics:
- All available metrics in SonarQube
- All active projects and their metrics and tags
- The list of tags used to use tag filter in the dashboards

Two sample dashboard definitions are provided as well:
- Detailed dashboard
  - User is able to select one project, pre-filtering by tag
  - For a given project, it displays the last value of 4 most common rates: Reliability rating, Security rating, Technical Debt rating & Cove coverage   
  - For a given project, it displays the historical value of 4 most common metrics: bugs, vulnerabilities, code coverage & code smells

- Executive dashboard
  - User is able to select one tag
  - For a given tag, it displays the historical value of 4 most common metrics for all the projects with that tag: bugs, vulnerabilities, code coverage & code smells

Constraints:
- Proper tagging system is highly encouraged in SonarQube. Project with no tag won't be displayed as the pre-filter is done by tags.

### How to use

First make sure there is communication and be able to authenticate to Sonarqube:
```
curl -XGET -u {USER}:{PASSWORD} https://mysonarqube.example.com
```
> Where {USER} and {PASSWORD}, replace with values that make sense in your reality.

### External values required to authenticate to the API
Export the environment variables to the values required to connect to Sonarqube. In the file **config.py**, the variables are decoded:
- SONAR_URL
- SONAR_USER
- SONAR_PASSWORD

To do this, run (Linux):
```
export SONAR_URL=https://mysonarqube.example.com
export SONAR_USER={USER}
export SONAR_PASSWORD={PASSWORD}
```
Or in Windows:
```
$env:SONAR_URL = 'https://mysonarqube.example.com'
$env:SONAR_USER = '{USER}'
$env:SONAR_PASSWORD = '{PASSWORD}'
```
> Where {USER} and {PASSWORD} must be the credentials of an authorized SonarQube account

Future optional values (not yet implemented):
- MAX_PROJECTS
- MAX_METRICS

### Deployment using Docker:
1. Build the image from the repo:
`docker build https://github.com/afernandezrios90/sonarqube-prometheus-exporter.git -t {image_tag}`
2. Run the image setting the environment variables:
`docker run -d -p 9120:9120 -e SONAR_URL=<sonar_url> -e SONAR_USER=<user> -e SONAR_PASSWORD=<password> {image_tag}`

### Current limitations
The current code supports reading a maximum of:
- 250 different projects
- 150 different metrics

However, SonarQube API allow higher limits, and they can be modified in the code. Maximum values can be passed as environment variables in future releases. 

### Add or remove Sonarqube metrics

In the **config.py** file, you will find a variable named **SUPPORTED_KEYS**, which loads an array of dicts containing the domain and keys that are captured by the script. If you just want to add a metric, identify your domain and then add it according to your domain. You can also add new ones as there is no restriction on the current ones.

> **Attention:** non-numeric metrics will be collected, but Prometheus will not support the values.
> https://github.com/prometheus/prometheus/issues/2227

### Metric naming

Prometheus, as a best practice, includes a value for documentation and Sonarqube natively exposes descriptions of each metric. Thus, the description of Sonarqube was addressed as documentation of Prometheus.

Each metric will have its name preserved by just adding the prefix *"sonar _"*, making it easy to identify in Prometheus.

## Grafana

Within my reality, not all metrics were used, but some that made sense at the moment include in a dashboard.

In this dashboard, projects are captured from the *sonar_bugs* metric and collecting the project key. You can view all metrics, only one or more than one.

Import the *grafana_dashboard.json* file, changing the DataSource to your reality.

### Dashboard screenshot

Simple dashboard with the possibility to filter by projects. For each selected project, a Gauge graph will be added and the others with line graphs will have one more line with that value. You can select all projects.

![Simple dashboard](dashboard_screenshot/simple_dashboard_project_filter.jpg)
