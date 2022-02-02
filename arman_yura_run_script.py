import click
import os
from os.path import dirname
from arman_yura_configs.configs import INTERNAL_ID
from arman_yura import Scraper, XMLGenerator
from arman_yura_utils.utils import set_json

# last = "Lee"
# first = "Derrick"
# middle = "Tirrell"
# birth = ""

# last = "Candler"
# first = "James"
# middle = ""
# birth = "07/23/1954"

# last = "Williams"
# first = "Willie"
# middle = "Charles"
# birth = ""

# last = "Williams"
# first = "Billy"
# middle = "Ray"
# birth = ""

@click.command()
@click.option(
    "-fn",
    "--first_name",
    required=True,
    default='Candler',
    help="First name of the person",
    type=str,
)
@click.option(
    "-ln",
    "--last_name",
    default="James",
    required=True,
    help="Last Name of the person",
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
    default="07/23/1954",
    required=False,
    help="Date of birth of the person",
    type=str,
)
@click.option(
    "-id",
    "--internalid",
    required=False,
    default=INTERNAL_ID,
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

    desired_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], "arman_yura_final_reports", f"{last_name}_{first_name}_bari_or_dzez")

    try:
        os.mkdir(desired_path)
    except:
        print('The folder already exists so we just continue to set json and xml files')

    set_json(input_path=desired_path, name=first_name, surname=last_name, input_dict=detailed_scraped_dictionary)

    xml_generator = XMLGenerator()
    general_dictionary, all_cases_list = xml_generator.generate_final_xml(detailed_scraped_dictionary)
    xml_generator.set_xml(firstname=first_name, lastname=last_name, general_dict=general_dictionary,
                          cases_list=all_cases_list)

    print(f'The xml file is set')

if __name__ == '__main__':
    scrape_data()
