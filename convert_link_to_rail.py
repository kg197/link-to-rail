"""(c) Copyright 2019. DataXu, Inc. All Rights Reserved."""
import argparse
import csv
import re
import sys
import xml.etree.ElementTree as Tree

# Choose the right HTML parser based on python version
if sys.version_info[0] == 2:
    from HTMLParser import HTMLParser

if sys.version_info[0] == 3:
    from html.parser import HTMLParser

HTML_PARSER = HTMLParser()


def strip_html(data):
    """
    Strip HTML tags
    :param data: Input string with HTML elements
    :return: Stripped output string
    """
    pattern = re.compile(r'<.*?>')
    return pattern.sub('', data)


def get_test_summary(xml):
    """
    Get test summary data
    :param xml: XML object
    :return: Summary and pre-conditions data
    """
    if xml.find('summary').text:
        summary = xml.find('summary').text
    else:
        summary = ''

    if xml.find('preconditions').text:
        pre_conditions = xml.find('preconditions').text
    else:
        pre_conditions = ''

    preconditions = summary + pre_conditions
    formatted_preconditions = strip_html(HTML_PARSER.unescape(preconditions).encode('utf-8'))

    return formatted_preconditions


def get_test_steps(xml):
    """
    Get test steps and expected results
    :param xml: XML object
    :return: A list of steps and expected results
    """
    test_steps = []
    expected_results = []
    number = ""
    step = ""

    if xml.find('steps') is not None:
        for steps in xml.find('steps'):
            if steps.find('step_number').text is not None:
                number = strip_html(HTML_PARSER.unescape(steps.find('step_number').text).encode('utf-8'))
            if steps.find('actions').text is not None:
                step = strip_html(HTML_PARSER.unescape(steps.find('actions').text).encode('utf-8'))

            test_steps.append(number.strip() + '. ' + step.strip() + "\n")

            if steps.find('expectedresults').text is not None:
                expected = strip_html(HTML_PARSER.unescape(steps.find('expectedresults').text).encode('utf-8'))
                expected_results.append(re.sub('\t+', ' ', number.strip() + '. ' + expected.strip() + "\n"))

    return [test_steps, expected_results]


def convert_xml_to_csv(input_file, output_file):
    """
    Convert XML file to CSV
    :param input_file: Input XML
    :param output_file: Output CSV
    :return:
    """
    # Parse the XML file
    tree = Tree.parse(input_file)
    root = tree.getroot()

    # Open a blank file for writing
    with open(output_file, 'w') as test_case_data:
        # create the csv writer object
        csv_writer = csv.writer(test_case_data)

        count = 0
        for test_cases in root.iter('testcase'):
            test_case_info = []

            # Increment the counter after writing header data
            if count == 0:
                csv_writer.writerow(['Title', 'Preconditions', 'Steps', 'Expected Results'])
                count += 1

            # Get the test name
            test_case_info.append(strip_html(HTML_PARSER.unescape(test_cases.get('name').encode('utf-8'))))

            # Get test name and pre conditions
            test_case_info.append(re.sub('\t+', ' ', get_test_summary(test_cases)))

            # Get test steps and expected results
            test_steps, expected_results = get_test_steps(test_cases)

            # Aggregate all related test steps and expected results
            if test_steps is not None and expected_results is not None:
                format_step = ''
                for each_step in test_steps:
                    format_step = format_step + each_step
                test_case_info.append(format_step)

                result = ''
                for each_result in expected_results:
                    result = result + each_result
                test_case_info.append(result)
            else:
                test_case_info.append(' ')
                test_case_info.append(' ')

            # Write test data in CSV file
            csv_writer.writerow(test_case_info)

def main():
    """
    main entry point to the tool
    :return:
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Convert TestLink XML file to TestRail CSV")
    parser.add_argument('-i', '--input_xml', required=True, help="TestLink Input XML file path")
    parser.add_argument('-o', '--output_csv', required=True, help="TestRail out CSV file name")

    args = parser.parse_args()

    # Calling convert XML to CSV function
    convert_xml_to_csv(input_file=args.input_xml, output_file=args.output_csv)


if __name__ == "__main__":
    main()
