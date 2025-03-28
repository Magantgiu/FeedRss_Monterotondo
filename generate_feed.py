import csv
import logging
from datetime import datetime
from feedgen.feed import FeedGenerator
import os

def setup_logging():
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rss_generator.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        logger.info("Logging is set up.")
        return logger
    except Exception as e:
        print(f"Failed to set up logging: {e}")
        raise

def generate_rss_feed(input_csv_path, output_rss_path):
    logger = setup_logging()
    try:
        fg = FeedGenerator()
        fg.title('Albo Pretorio Monterotondo')
        fg.link(href='https://servizionline.hspromilaprod.hypersicapp.net/cmsmonterotondo/portale/albopretorio/albopretorioconsultazione.aspx?P=400')
        fg.description('Feed RSS ufficiale degli avvisi pubblici')
        fg.language('it')

        entries_added = 0
        with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_columns = ['DATA_INIZIO_PUBBLICAZIONE', 'OGGETTO', 'MITTENTE', 'DATA_ATTO_ORIGINALE']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV is missing one or more required columns: {required_columns}")

            for row in reader:
                try:
                    parse_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
                    parsed_date = None
                    for date_format in parse_formats:
                        try:
                            parsed_date = datetime.strptime(row['DATA_INIZIO_PUBBLICAZIONE'], date_format)
                            break
                        except ValueError:
                            continue
                    if not parsed_date:
                        logger.warning(f"Could not parse date for entry: {row['OGGETTO']} - Date: {row['DATA_INIZIO_PUBBLICAZIONE']}")
                        continue

                    entry = fg.add_entry()
                    entry.title(row['OGGETTO'])
                    entry.link(href='https://servizionline.hspromilaprod.hypersicapp.net/cmsmonterotondo/portale/albopretorio/albopretorioconsultazione.aspx?P=400')  # Update this with the actual URL if available
                    entry.pubDate(parsed_date)
                    entry.description(f"{row['MITTENTE']} - {row['DATA_ATTO_ORIGINALE']}")
                    entries_added += 1
                    logger.info(f"Added entry: {row['OGGETTO']}")
                except KeyError as ke:
                    logger.error(f"Missing key in CSV row: {ke}")
                except Exception as e:
                    logger.error(f"Error processing row: {e}")

        os.makedirs(os.path.dirname(output_rss_path), exist_ok=True)
        fg.rss_file(output_rss_path)
        fg.atom_file(output_rss_path.replace('.xml', '_atom.xml'))

        logger.info(f"RSS feed generated successfully. Total entries: {entries_added}")
        logger.info(f"Output files: {output_rss_path} and {output_rss_path.replace('.xml', '_atom.xml')}")
    except FileNotFoundError:
        logger.error(f"Input CSV file not found: {input_csv_path}")
    except PermissionError:
        logger.error(f"Permission denied when trying to read {input_csv_path} or write {output_rss_path}")
    except Exception as e:
        logger.error(f"Unexpected error in RSS feed generation: {e}")

def main():
    input_csv_path = 'albopretorio.csv'
    output_rss_path = 'docs/feed.xml'
    generate_rss_feed(input_csv_path, output_rss_path)

if __name__ == '__main__':
    main()
