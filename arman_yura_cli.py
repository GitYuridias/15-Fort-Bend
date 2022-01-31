import click
import time
from arman_yura_configs.configs import INTERNAL_ID

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

@click.group("scrape")
def commands():
    """
    Package's scrapers command line interface with the help of which you can scrape desired content.
    """
    pass


@commands.command(
    "scrape_data", help="Scraping the desired data from the specified website"
)
@click.option(
    "-id",
    "--internalID",
    required=False,
    default=INTERNAL_ID,
    help="Internal ID specified for each case",
    type=str,
)
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
def scrape_data(
    internalID,
    first_name,
    last_name,
    middle_name,
    date_of_birth,
):

    # if type_of_url == "phishing":
    #
    #     data = RawScrapeDateDataset().read(read_phishing_data, start_date, end_date)
    #
    # elif type_of_url == "none_phishing":
    #
    #     data = RawSQLDateDataset().read(start_date, end_date)
    #     data = BenignDataTransformer().transform(data)
    #     data['date'] = [end_date] * len(data)

    else:
        raise click.ClickException("Wrong type of url specified")

    RawSQLDateDataset().write(data)
    logging.info('The end of get data stage')


