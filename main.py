import csv


def main():
    with open("authors_2.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["name"])
        for i in range(1_500_000):
            writer.writerow({"name": f"Author {i}"})


if __name__ == "__main__":
    main()
