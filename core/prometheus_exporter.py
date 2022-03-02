import enum
from posixpath import split
from prometheus_client.core import GaugeMetricFamily
import prometheus_client as prom
import time
from sonarqube_exporter import get_all_projects_with_metrics

class CustomSonarExporter:

    def __init__(self):
        pass

    def collect(self):
        projects = get_all_projects_with_metrics()

        tags = set()

        for project in projects:

            # First of all extract the languages used 
            lang_used = [lang for lang in project.metrics if lang.key == 'ncloc_language_distribution']
            if len(lang_used):
                lang_used = lang_used[0].values[0][1]
                lang_used = lang_used.split(';')
                lang_used = list(map(lambda s: s.split('=')[0], lang_used))
            else:
                lang_used = ''
            
            for metric in project.metrics:
                label_list = ['key', 'name', 'languages']
                label_values = []
                value_to_set = None

                # Set the common labels to all metrics (project ID, project key, project name & languages used)
                label_values.append(project.key)
                label_values.append(project.name)
                label_values.append("|".join(lang_used))

                # If the project has associated tags, add a string with the tags as label as well
                if len(project.tags):
                    label_list.append('tags')
                    label_values.append("|".join(project.tags))
                    # Add any new tags to the tag list (for later usage)
                    tags.update(project.tags)

                # Special case: for 'ncloc_language_distribution', generate one 'lines_per_language' metric per language
                # Sample: [('value','cs=10846;scss=293;ts=4436')]
                if metric.key == 'ncloc_language_distribution':
                    languages_metrics = metric.values[0][1].split(';')
                    languages = [i.split('=')[0] for i in languages_metrics]
                    l_metrics = [i.split('=')[1] for i in languages_metrics]

                    label_list_lang = label_list.copy()
                    label_list_lang.append('language')
                    gauge = GaugeMetricFamily(
                        name='sonar_lines_per_language',
                        documentation=metric.description,
                        labels=label_list_lang
                        )
                    
                    for i, v in enumerate(languages):
                        label_values_lang = label_values.copy()
                        label_values_lang.append(v)
                        
                        gauge.add_metric(
                            labels=label_values_lang,
                            value=l_metrics[i]
                        )
                        yield gauge

                else:
                    for metric_value in metric.values:
                        if metric_value[0] == 'value':
                            value_to_set = metric_value[1]
                        else:
                            label_list.append(metric_value[0])
                            label_values.append(metric_value[1])

                    gauge = GaugeMetricFamily(
                        name="sonar_{}".format(metric.key),
                        documentation=metric.description,
                        labels=label_list
                    )

                    gauge.add_metric(
                        labels=label_values,
                        value=value_to_set
                    )
                    yield gauge

        # Expose also the tag list as metrics with a dummy value "1" to be able to filter in Grafana by tags
        gauge_tag_list = GaugeMetricFamily(
            name="sonar_tag_index",
            documentation="Tag index for filtering",
            labels=['tag']
            )
        for tag in tags:
            gauge_tag_list.add_metric(labels=[tag],value=1)
        yield gauge_tag_list


if __name__ == "__main__":
    custom_exporter = CustomSonarExporter()
    prom.REGISTRY.register(custom_exporter)
    prom.start_http_server(9120)

    while True:
        time.sleep(2)