import datetime


class NewsFeed:
    FILE_NAME = "news_feed.txt"

    @staticmethod
    def write_to_file(content):
        """Appends the formatted content to the file."""
        with open(NewsFeed.FILE_NAME, "a", encoding="utf-8") as file:
            file.write(content + "\n\n")

    def add_news(self):
        """Handles adding a news record."""
        text = input("Enter News text: ")
        city = input("Enter City: ")
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        news_entry = f"News -------------------------\n{text}\nCity: {city}, Date: {date}"
        self.write_to_file(news_entry)
        print("News added successfully!\n")

    def add_private_ad(self):
        """Handles adding a private ad record."""
        text = input("Enter Ad text: ")
        exp_date_str = input("Enter Expiration Date (YYYY-MM-DD): ")
        try:
            exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
            days_left = (exp_date - datetime.datetime.now()).days
            ad_entry = f"Private Ad ------------------\n{text}\nExpires on: {exp_date_str}, Days left: {days_left}"
            self.write_to_file(ad_entry)
            print("Private Ad added successfully!\n")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.\n")

    def add_motivation_quote(self):
        """Handles adding a motivational quote."""
        quote = input("Enter a Motivational Quote: ")
        author = input("Enter Author's Name: ")
        quote_entry = f"Motivational Quote -----------\n\"{quote}\"\n- {author}"
        self.write_to_file(quote_entry)
        print("Motivational Quote added successfully!\n")

    def run(self):
        while True:
            print("\nChoose record type:")
            print("1 - News")
            print("2 - Private Ad")
            print("3 - Motivational Quote")
            print("4 - Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.add_news()
            elif choice == "2":
                self.add_private_ad()
            elif choice == "3":
                self.add_motivation_quote()
            elif choice == "4":
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.\n")


if __name__ == "__main__":
    app = NewsFeed()
    app.run()
