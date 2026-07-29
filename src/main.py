import logger as lg
import transformer
import loader


def main():
    lg.log_info("=== UTel BI Pipeline: starting ===")

    lg.log_info("Step 1/2: Transforming raw data...")
    transformer.main()
    lg.log_ok("Transformation complete.")

    lg.log_info("Step 2/2: Loading cleaned data into database...")
    loader.load(data_dir=str(transformer.CLEAN_DIR))
    lg.log_ok("Loading complete.")

    lg.log_info("=== UTel BI Pipeline: finished ===")


if __name__ == "__main__":
    main()
