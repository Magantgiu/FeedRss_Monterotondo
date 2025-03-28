#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import logging
from datetime import datetime
from feedgen.feed import FeedGenerator
import os

def setup_logging():
    """Configure logging for the RSS feed generation process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rss_generator.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def generate_rss_feed(input_csv_path, output_rss_path):
    """
    Generate an RSS feed from a CSV file.
    
    :param input_csv_path: Path to the input CSV file
    :param output_rss_path: Path to save the output RSS XML file
    """
    logger = setup_logging()
    
    try:
        # Create feed generator
        fg = FeedGenerator()
        fg.title('Albo Pretorio Monterotondo')
        fg.link(href='https://comune.monterotondo.rm.it/albo')
        fg.description('Feed RSS ufficiale degli avvisi pubblici')
        fg.language('it')
        
        # Read CSV and add entries
        entries_added = 0
        with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate required columns
            required_columns = ['Titolo', 'URL', 'Data', 'Descrizione']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV is missing one or more required columns: {required_columns}")
            
            # Process each row
            for row in reader:
                try:
                    # Validate and parse date
                    try:
                        # Attempt to parse date in multiple common formats
                        parse_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
                        parsed_date = None
                        for date_format in parse_formats:
                            try:
                                parsed_date = datetime.strptime(row['Data'], date_format)
                                break
                            except ValueError:
                                continue
                        
                        if not parsed_date:
                            logger.warning(f"Could not parse date for entry: {row['Titolo']} - Date: {row['Data']}")
                            continue
                    except Exception as date_error:
                        logger.error(f"Error parsing date for {row['Titolo']}: {date_error}")
                        continue
                    
                    # Create feed entry
                    entry = fg.add_entry()
                    entry.title(row['Titolo'])
                    entry.link(href=row['URL'])
                    entry.pubDate(parsed_date)
                    entry.description(row['Descrizione'])
                    
                    entries_added += 1
                
                except KeyError as ke:
                    logger.error(f"Missing key in CSV row: {ke}")
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_rss_path), exist_ok=True)
        
        # Generate RSS feed files
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
    """Main function to generate RSS feed."""
    input_csv_path = 'albopretorio.csv'
    output_rss_path = 'feed.xml'
    generate_rss_feed(input_csv_path, output_rss_path)

if __name__ == '__main__':
    main()
