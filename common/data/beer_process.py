# Ben Kabongo - MIA Paris-Saclay x Onepoint
# NLP & RecSys - May 2024

# Beer datasets: loading and formatting data

import argparse
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
from tqdm import tqdm


def rescale(x, a, b, c, d):
    return c + (d - c) * ((x - a) / (b - a))


def process_dataset(args):
    columns = {
        "user_id": "beer/brewerId",
        "user_name": "review/profileName",
        "item_id": "beer/beerId",
        "item_name": "beer/name",
        "ABV": "beer/ABV",
        "style": "beer/style",
        "review": "review/text",
        "timestamp": "review/time",
        "rating": "review/overall",
        "appearance": "review/appearance",
        "aroma": "review/aroma",
        "palate": "review/palate",
        "taste": "review/taste",
    }
    aspects = ["appearance", "aroma", "palate", "taste"]

    output_dir = os.path.join(args.output_base_dir, args.dataset_name)
    os.makedirs(output_dir, exist_ok=True)

    data_df_path  = os.path.join(output_dir, "data.csv")
    users_df_path = os.path.join(output_dir, "users.csv")
    items_df_path = os.path.join(output_dir, "items.csv")

    data = []
    users = []
    items = []

    with open(args.dataset_file, 'r', encoding="utf-8") as fp:
        for line in tqdm(fp, args.dataset_name, colour="green", total=args.n_lines):
            row = json.loads(line.strip())
            if not bool(row):
                continue
            
            users.append(
                dict(
                    user_id=row[columns["user_id"]],
                    user_name=row[columns["user_name"]]
                )
            )

            items.append(
                dict(
                    item_id=row[columns["item_id"]],
                    name=row[columns["item_name"]],
                    style=row[columns["style"]],
                    abv=row[columns["ABV"]],
                    description=(
                        f'{row[columns["item_name"]]} ; ' +
                        f'Style: {row[columns["style"]]} ' +
                        f'ABV: {row[columns["ABV"]]}'
                    )
                )
            )

            sample = dict(
                user_id=row[columns["user_id"]],
                item_id=row[columns["item_id"]],
                timestamp=row[columns["timestamp"]],
                review=row[columns["review"]]
            )
            sample["rating"] = rescale(
                float(row[columns["rating"]].split("/")[0]),
                0, float(row[columns["rating"]].split("/")[1]),
                args.min_rating, args.max_rating
            )
            for aspect in aspects:
                sample[aspect] = rescale(
                    float(row[columns[aspect]].split("/")[0]),
                    0, float(row[columns[aspect]].split("/")[1]),
                    args.aspect_min_rating, args.aspect_max_rating
                )
            data.append(sample)

    data_df = pd.DataFrame(data)
    users_df = pd.DataFrame(users)
    items_df = pd.DataFrame(items)

    data_df.to_csv(data_df_path)
    users_df.to_csv(users_df_path)
    items_df.to_csv(items_df_path)

    if args.verbose:
        print(args.dataset_name)
        print("Data:")
        print(data_df.sample(n=2))
        print()
        print("Users:")
        print(users_df.sample(n=2))
        print()
        print("Items:")
        print(items_df.sample(n=2))

    user_reviews_count = data_df.groupby('user_id').size()
    plt.figure(figsize=(10, 6))
    sns.histplot(user_reviews_count, bins=50, kde=True)
    plt.title('Number of reviews/ratings per user')
    plt.xlabel('Number of reviews/ratings')
    plt.ylabel('Number of users')
    plt.savefig(os.path.join(output_dir, "users_stats.png"))

    item_reviews_count = data_df.groupby('item_id').size()
    plt.figure(figsize=(10, 6))
    sns.histplot(item_reviews_count, bins=50, kde=True)
    plt.title('Number of reviews/ratings per item')
    plt.xlabel('Number of reviews/ratings')
    plt.ylabel('Number of items')
    plt.savefig(os.path.join(output_dir, "items_stats.png"))

    plt.figure(figsize=(10, 6))
    sns.histplot(data_df['rating'], bins=5, kde=True)
    plt.title('Rating distribution')
    plt.xlabel('Rating')
    plt.ylabel('Number of reviews')
    plt.savefig(os.path.join(output_dir, "ratings_stats.png"))
    
    for aspect in aspects:
        plt.figure(figsize=(10, 6))
        sns.histplot(data_df[aspect], bins=5, kde=True)
        plt.title('Rating distribution')
        plt.xlabel(aspect)
        plt.ylabel('Number of reviews')
        plt.savefig(os.path.join(output_dir, f"{aspect}_stats.png"))

    review_length = data_df['review'].apply(lambda x: len(str(x).split()))
    plt.figure(figsize=(10, 6))
    sns.histplot(review_length, bins=50, kde=True)
    plt.title('Review length distribution')
    plt.xlabel('Review length')
    plt.ylabel('Number of reviews')
    plt.savefig(os.path.join(output_dir, "reviews_stats.png"))

    description_length = items_df['description'].apply(lambda x: len(str(x).split()))
    plt.figure(figsize=(10, 6))
    sns.histplot(description_length, bins=50, kde=True)
    plt.title('Description length distribution')
    plt.xlabel('Description length')
    plt.ylabel('Number of descriptions')
    plt.savefig(os.path.join(output_dir, "descriptions_stats.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--dataset_file", type=str, default="") #"Datasets\\ASBA\\Beer\\ratebeer_.json"
    parser.add_argument("--output_base_dir", type=str, default="") #"Datasets\\ASBA\\Beer"
    parser.add_argument("--dataset_name", type=str, default="") #"RateBeer"
    parser.add_argument("--n_lines", type=int, default=0) #2_778_708

    parser.add_argument("--min_rating", type=float, default=1.0)
    parser.add_argument("--max_rating", type=float, default=5.0)
    parser.add_argument("--aspect_min_rating", type=float, default=1.0)
    parser.add_argument("--aspect_max_rating", type=float, default=5.0)
    
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
    parser.set_defaults(verbose=True)
    args = parser.parse_args()

    process_dataset(args)
    