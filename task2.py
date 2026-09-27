import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import requests
import matplotlib.pyplot as plt


def fetch_text(url: str) -> str:
    """
    Завантажує текст за заданою URL-адресою.
    """
    response = requests.get(
        url,
        timeout=15,
    )

    response.raise_for_status()

    return response.text


def map_function(word: str):
    """
    Map-функція:
    кожне слово перетворює у пару (word, 1).
    """
    return word, 1


def shuffle_function(mapped_values):
    """
    Групує однакові слова.
    """
    shuffled = defaultdict(list)

    for key, value in mapped_values:
        shuffled[key].append(value)

    return shuffled


def reduce_function(item):
    """
    Reduce-функція:
    підраховує кількість появ слова.
    """
    word, values = item

    return word, sum(values)


def map_reduce(text: str):
    """
    Виконує MapReduce для підрахунку частоти слів.
    Використовує багатопотоковість.
    """
    words = re.findall(
        r"\b[a-zA-Zа-яА-ЯіїєґІЇЄҐ']+\b",
        text.lower(),
    )

    with ThreadPoolExecutor() as executor:
        mapped_values = list(
            executor.map(
                map_function,
                words,
            )
        )

    shuffled_values = shuffle_function(
        mapped_values
    )

    with ThreadPoolExecutor() as executor:
        reduced_values = list(
            executor.map(
                reduce_function,
                shuffled_values.items(),
            )
        )

    return dict(reduced_values)


def visualize_top_words(
    word_counts: dict,
    top_n: int = 10,
) -> None:
    """
    Візуалізує top N найчастіше вживаних слів.
    """
    sorted_words = sorted(
        word_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:top_n]

    words = [
        word
        for word, _ in sorted_words
    ]

    counts = [
        count
        for _, count in sorted_words
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.barh(
        words,
        counts,
    )

    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(
        f"Top {top_n} most frequent words"
    )

    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()


def main():
    url = input(
        "Enter URL with text: "
    )

    try:
        text = fetch_text(url)

        word_counts = map_reduce(text)

        visualize_top_words(
            word_counts,
            top_n=10,
        )

    except requests.RequestException as error:
        print(
            f"Error while downloading text: {error}"
        )

    except Exception as error:
        print(
            f"Unexpected error: {error}"
        )


if __name__ == "__main__":
    main()