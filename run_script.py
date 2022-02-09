import click
import os
from os.path import dirname
from data_scraper import Scraper, XMLGenerator
from utils.utils import set_json

@click.command()
@click.option(
    "-fn",
    "--first_name",
    required=True,
    default='',
    help="First name of the person aka for example, -fn 'James' ",
    type=str,
)
@click.option(
    "-ln",
    "--last_name",
    default='',
    required=True,
    help="Last Name of the person aka for example, -ln 'Candler' ",
    type=str,
)
@click.option(
    "-mn",
    "--middle_name",
    type=str,
    default="",
    required=False,
    help="If the person has also middle name we can specify that",
)
@click.option(
    "-dob",
    "--date_of_birth",
    default="",
    required=False,
    help="Date of birth of the person where format must be 'MM/DD/YYYY' ",
    type=str,
)
@click.option(
    "-id",
    "--internalid",
    required=True,
    default="",
    help="Internal ID specified for each case",
    type=str,
)
def scrape_data(
    first_name,
    last_name,
    middle_name,
    date_of_birth,
    internalid
):

    scraper = Scraper(first_name=first_name, last_name=last_name,
                      middle_name=middle_name, date_of_birth=date_of_birth, internal_id=internalid)
    scraper.submit_form()
    primary_dictionary = scraper.get_primary_dict()
    detailed_scraped_dictionary = scraper.scrape_details(primary_dictionary)
    scraper.quit_driver()

    desired_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], "final_reports", f"{internalid}")

    try:
        os.mkdir(desired_path)
    except:
        print('The folder already exists so we just continue to set json and xml files')

    set_json(input_path=desired_path, internal_id=internalid, input_dict=detailed_scraped_dictionary)

    xml_generator = XMLGenerator()
    general_dictionary, all_cases_list = xml_generator.generate_final_xml(detailed_scraped_dictionary)
    xml_generator.set_xml(internal_id=internalid, general_dict=general_dictionary,
                          cases_list=all_cases_list)

    print(f'The xml file is set')


if __name__ == '__main__':
    scrape_data()
