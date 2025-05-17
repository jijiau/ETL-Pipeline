from utils.extract import scrape_main

if __name__ == "__main__":
    data = scrape_main()
    print("Contoh data:")
    for item in data[:5]:
        print(item)
