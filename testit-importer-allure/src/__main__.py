from testit_importer_allure.reader import AttributeReader
from testit_importer_allure.utils import form_steps
from testit_importer_allure.utils import form_labels_namespace_classname_workitems_id
from testit_importer_allure.utils import form_links
from testit_importer_allure.utils import form_setup_teardown
from testit_importer_allure.utils import form_parameters
from testit_importer_allure.utils import get_attachment
from testit_api_client.api import Api
from testit_api_client.json_fixture import JSONFixture
from datetime import datetime


def console_main():
    reader = AttributeReader()
    data_tests, data_before_after = reader.get_attr()

    if data_tests:
        data_before_after = dict(sorted(data_before_after.items(), key=lambda x: x[0]))
        requests = Api(reader.get_url(), reader.get_privatetoken())
        tests_results_data = []

        for history_id in data_tests:
            prefix = '' if 'uuid' in data_tests[history_id] else '@'

            labels, namespace, classname, workitems_id = form_labels_namespace_classname_workitems_id(data_tests[history_id]['labels'])

            attachments = get_attachment(requests, data_tests[history_id]['attachments'], reader.get_path()) if 'attachments' in data_tests[history_id] else []

            setup, results_setup, teardown, results_teardown = form_setup_teardown(data_before_after, data_tests[history_id]['uuid'] if
                                                                                        'uuid' in data_tests[history_id] else None, requests, reader.get_path())

            if 'steps' in data_tests[history_id]:
                steps, results_steps = form_steps(data_tests[history_id]['steps'], requests, reader.get_path())
            else:
                steps = []
                results_steps = []

            links = form_links(data_tests[history_id]['links']) if 'links' in data_tests[history_id] else []

            outcome = data_tests[history_id][f'{prefix}status'].title() if data_tests[history_id][f'{prefix}status'] in ('passed', 'skipped') else 'Failed'

            autotest = requests.get_autotest(history_id, reader.get_project_id()).json()

            if not autotest:
                autotest_id = requests.create_autotest(
                    JSONFixture.create_autotest(
                        history_id,
                        reader.get_project_id(),
                        data_tests[history_id]['name'],
                        steps,
                        setup,
                        teardown,
                        namespace,
                        classname,
                        None,
                        data_tests[history_id]['description'] if 'description' in data_tests[history_id] else None,
                        links,
                        labels
                    )
                )
            else:
                autotest_id = autotest[0]['id']

                if outcome == 'Passed':
                    requests.update_autotest(
                        JSONFixture.update_autotest(
                            history_id,
                            reader.get_project_id(),
                            data_tests[history_id]['name'],
                            autotest_id,
                            steps,
                            setup,
                            teardown,
                            namespace,
                            classname,
                            None,
                            data_tests[history_id]['description'] if 'description' in data_tests[history_id] else None,
                            links,
                            labels
                        )
                    )
                else:
                    requests.update_autotest(
                        JSONFixture.update_autotest(
                            history_id,
                            reader.get_project_id(),
                            autotest[0]['name'],
                            autotest_id,
                            autotest[0]['steps'],
                            autotest[0]['setup'],
                            autotest[0]['teardown'],
                            autotest[0]['namespace'],
                            autotest[0]['classname'],
                            autotest[0]['title'],
                            autotest[0]['description'],
                            links,
                            autotest[0]['labels']
                        )
                    )

            for workitem_id in workitems_id:
                requests.link_autotest(autotest_id, workitem_id)

            tests_results_data.append(
                JSONFixture.set_results_for_testrun(
                    history_id,
                    reader.get_configuration_id(),
                    outcome,
                    results_steps,
                    results_setup,
                    results_teardown,
                    data_tests[history_id]['statusDetails']['trace'] if
                        'statusDetails' in data_tests[history_id] and data_tests[history_id]['statusDetails'] and 'trace' in data_tests[history_id]['statusDetails'] else None,
                    attachments,
                    form_parameters(data_tests[history_id]['parameters']) if 'parameters' in data_tests[history_id] else None,
                    links,
                    (int(data_tests[history_id][f'{prefix}stop']) - int(data_tests[history_id][f'{prefix}start'])) if f'{prefix}stop' in data_tests[history_id] else 0,
                    None,
                    data_tests[history_id]['statusDetails']['message'] if
                        'statusDetails' in data_tests[history_id] and data_tests[history_id]['statusDetails'] and 'message' in data_tests[history_id]['statusDetails'] else None
                )
            )

        testrun_id = requests.create_testrun(JSONFixture.create_testrun(reader.get_project_id(), f'AllureRun {datetime.today().strftime("%d %b %Y %H:%M:%S")}'))

        if tests_results_data:
            requests.set_results_for_testrun(
                testrun_id,
                tests_results_data
            )


if __name__ == "__main__":
    console_main()
