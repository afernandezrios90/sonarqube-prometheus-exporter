import requests
import logging
from config import Config

# Web API Documentation: http://your-sonarqube-url/web_api

CONF = Config()

class SonarExporter:

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.base_url = CONF.sonar_url

    def _request(self, endpoint):
        req = requests.get("{}/{}".format(self.base_url, endpoint), auth=(self.user, self.password))
        if req.status_code != 200:
            return req.status_code
        else:
            return req.json()

    def get_all_projects(self):
        return self._request(endpoint='api/components/search_projects?ps=250')

    def get_all_metrics(self):
        return self._request(endpoint='api/metrics/search?ps=150')

    def get_measures_component(self, component_key, metric_key):
        return self._request(endpoint="api/measures/component?component={}&metricKeys={}".format(component_key, metric_key))

    def get_code_smells(self, component_key):
        return self._request(endpoint="api/issues/search?componentKeys={}&types=CODE_SMELL&statuses=OPEN,REOPENED&facets=severities&facetMode=count".format(component_key))

class Project:

    def __init__(self, key):
        self.key = key
        self._metrics = None
        self._name = None
        self._tags = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = value

    def organize_measures(self, metrics : list):
        # Self is the object of class Project, metrics is the list of available metrics
        metric_obj_list = []
        # Iterate over the metrics measured for the project
        for metric in self.metrics['component']['measures']:
            if 'metric' in metric:
                m = Metric()
                tuple_list = []
                # Iterate on the available metrics, search the information of the metric that has been measued and fill in the metric object 
                for metric_obj in metrics:
                    if metric_obj.key == metric['metric']:
                        m.key = metric_obj.key
                        m.description = metric_obj.description
                        m.domain = metric_obj.domain
                # Transform the each individual metric (which is an object) into a tuple, then append all values except the metric name itself,
                # which is assigned to the metric key
                for met_tuples in self.transform_object_in_list_tuple(metric):
                    if met_tuples[0] == 'metric':
                        m.key = met_tuples[1]
                    else:
                        tuple_list.append(met_tuples)
                m.values = tuple_list
            metric_obj_list.append(m)
        self.metrics = metric_obj_list

    def transform_object_in_list_tuple(self, metric_object):
        # Transform object into tuple, example:
        # OLD --> {'metric': 'duplicated_lines_density','value': '11,4','bestValue': False}
        # NEW --> [('value','11,4'),('bestValue','False')]
        object_list_tuples = []
        for item in metric_object:
            if isinstance(metric_object[item], list):
                # Recursivity for allowing nested objects
                for obj in metric_object[item]:
                    object_list_tuples.extend(self.transform_object_in_list_tuple(metric_object=obj))
            else:
                obj_tuple = (str(item), str(metric_object[item]))
                object_list_tuples.append(obj_tuple)
        return object_list_tuples

    def organize_code_smells(self, code_smells):
        for code_smell in code_smells['facets'][0]['values']:
            # Create a new Metric object and format the information
            m = Metric()
            m.key = 'code_smells_' + code_smell['val'].lower()
            m.description = 'Number of code smells for severity: ' + code_smell['val']
            m.domain = 'Maintainability'
            m.values.append(('value',str(code_smell['count'])))
            # Append the metric to the list of existing metrics
            self.metrics.append(m)

class Metric:

    def __init__(self):
        self._key = None # Example 'sqale_debt_ratio'
        self._values = [] # Example [('value', '0.0), ('bestValue', 'True')]
        self._description = None # Example 'Ratio of the technical debt'
        self._domain = None # Example 'Maintainability'

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, value):
        self._values.extend(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value

def get_all_projects_with_metrics():
    projects = []
    metrics = []

    client = SonarExporter(CONF.sonar_user, CONF.sonar_password)
    all_projects = client.get_all_projects()
    all_metrics = client.get_all_metrics()

    for metric in all_metrics['metrics']:
        m = Metric()
        for item in CONF.supported_keys:
            if 'domain' in metric and metric['domain'] in item['domain']:
                if 'key' in metric and metric['key'] in item['keys']:
                    m.key = metric['key']
                    m.domain = metric['domain']
                    if 'description' in metric:
                        m.description = metric['description']
                    metrics.append(m)

    metrics_comma_separated = str()
    for metric in metrics:
        if metric.description:
            metrics_comma_separated = "{},{}".format(metric.key, metrics_comma_separated)


    for project in all_projects['components']:
        p = Project(key=project['key'])
        p.name = project['name']
        p.tags = project['tags']
        # Get the standard metrics
        p.metrics = client.get_measures_component(component_key=p.key, metric_key=metrics_comma_separated)
        p.organize_measures(metrics)
        # Get the code smells by severity
        code_smells = client.get_code_smells(component_key=p.key)
        p.organize_code_smells(code_smells)
        projects.append(p)

    return projects