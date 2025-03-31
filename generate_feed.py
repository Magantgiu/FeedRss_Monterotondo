import csv
import logging
from datetime import datetime
from feedgen.feed import FeedGenerator
import os
import uuid

def setup_logging():
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
    logger = setup_logging()
    
    # Debug: mostra il percorso completo e controlla l'esistenza del file
    logger.info(f"Percorso file CSV: {os.path.abspath(input_csv_path)}")
    logger.info(f"File esiste: {os.path.exists(input_csv_path)}")
    
    # Elenca i file nella directory corrente
    logger.info("Files nella directory corrente:")
    for filename in os.listdir('.'):
        logger.info(filename)
    try:
        fg = FeedGenerator()
        fg.title('Albo Pretorio Monterotondo')
        fg.link(href='https://servizionline.hspromilaprod.hypersicapp.net/cmsmonterotondo/portale/albopretorio/albopretorioconsultazione.aspx?P=400')
        fg.description('Feed RSS ufficiale degli avvisi pubblici')
        fg.language('it')
        
        # Add a unique identifier for the feed
        fg.id(f'urn:uuid:{uuid.uuid4()}')
        
        # Add additional feed metadata
        fg.generator('Monterotondo RSS Generator')
        fg.webMaster('webmaster@comune.monterotondo.rm.it')

        entries_added = 0
        with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
            # Usa il delimitatore pipe e specifica le colonne
            reader = csv.DictReader(csvfile, delimiter='|')
            
            required_columns = ['DATA_INIZIO_PUBBLICAZIONE', 'OGGETTO', 'MITTENTE', 'DATA_ATTO_ORIGINALE']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV is missing one or more required columns: {required_columns}")

            for row in reader:
                try:
                    parse_formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']
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

                    # Costruisci una descrizione più completa
                    description = f"Mittente: {row['MITTENTE']}"
                    if row['DATA_ATTO_ORIGINALE']:
                        description += f" - Data atto: {row['DATA_ATTO_ORIGINALE']}"
                    if row.get('NUMERO') and row.get('ANNO'):
                        description += f" - Rif. N. {row['NUMERO']}/{row['ANNO']}"

                    entry = fg.add_entry()
                    # Aggiungi un identificatore univoco per ogni entry
                    entry.id(f'urn:uuid:{uuid.uuid4()}')
                    entry.title(row['OGGETTO'])
                    entry.link(href='https://servizionline.hspromilaprod.hypersicapp.net/cmsmonterotondo/portale/albopretorio/albopretorioconsultazione.aspx?P=400')
                    # Converte la data in un oggetto con timezone UTC
                    from datetime import timezone
                    parsed_date_utc = parsed_date.replace(tzinfo=timezone.utc)
                    entry.pubDate(parsed_date_utc)
                    entry.description(description)
                    
                    entries_added += 1
                    logger.info(f"Added entry: {row['OGGETTO']}")
                
                except KeyError as ke:
                    logger.error(f"Missing key in CSV row: {ke}")
                except Exception as e:
                    logger.error(f"Error processing row: {e}")

        # Assicurati che la directory di output esista
        os.makedirs(os.path.dirname(output_rss_path), exist_ok=True)
        
        # Genera i feed
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
    # Usa un percorso assoluto
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_csv_path = os.path.join(base_path, 'albopretorio.csv')
    output_rss_path = os.path.join(base_path, 'feed.xml')
    
    # Stampa il percorso del file per debug
    print(f"Tentativo di leggere il file da: {input_csv_path}")
    
    generate_rss_feed(input_csv_path, output_rss_path)

if __name__ == '__main__':
    main()
