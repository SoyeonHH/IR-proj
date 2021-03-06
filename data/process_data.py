from itertools import product
import pickle
import json
from collections import defaultdict
from site import USER_SITE

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def rating_to_label(r):
    if r <= 2:
        return 0
    else:
        return 1


def main():

    with open('amazon_fashion_dataset_review.json', 'r') as f:
        data = json.load(f)
    
    data = pd.DataFrame(data)

    data['product'] = data['product'].astype(str)
    data['time'] = data['time'].astype(int)
    data['year'] = data['year'].astype(int)
    data['month'] = data['month'].astype(int)
    data['day'] = data['day'].astype(int)
    data['text'] = data['text'].astype(str)
    data['rating'] = data['rating'].astype(float)

    product_times = defaultdict(list)
    for product, year in zip(data['product'], data['year']):
        product_times[product].append(year)

    products = set()
    for product in product_times:
        t_2010_2018 = [y for y in product_times[product] if y >= 2010]
        if len(t_2010_2018) >= 10:
            products.add(product)

    data = data[(data['product'].isin(products)) & (data['year'] >= 2010)]

    data = data[data['text'].apply(lambda x: len(x.strip().split())) >= 10]
    data['text'] = data['text'].apply(lambda x: x.lower())
    data['label'] = data['rating'].apply(rating_to_label)
    data.drop_duplicates(subset=['text'], inplace=True)
    data.dropna(inplace=True)

    data.reset_index(inplace=True, drop=True)

    data = data[['product', 'time', 'year', 'month', 'day', 'text', 'rating', 'label']]

    # average number of tokens per text
    tl = []
    for t in data['text']:
        tl.append(len(t.split(' ')))
    tl = np.asarray(tl)

    print("The number of data points: ", len(data))
    print("The average of number of tokens per text: ", np.mean(tl))

    train_dev, test = train_test_split(data, test_size=0.2, random_state=123, stratify=data[['rating']])
    train, dev = train_test_split(train_dev, test_size=0.125, random_state=123, stratify=train_dev[['rating']])

    train.to_csv('amazon_fashion_train.csv', index=False)
    dev.to_csv('amazon_fashion_dev.csv', index=False)
    test.to_csv('amazon_fashion_test.csv', index=False)

    edge_set = set()
    products = set(data['product'])

    with open('amazon_fashion_dataset_product.json', 'r') as f:
        data_product = json.load(f)
    
    data_product = pd.DataFrame(data_product)
    c_product = data_product['product']
    c_related = data_product['related'].apply(lambda x: x.strip().split(', '))

    edge_set.update([(p, r) for p, rs in zip(c_product, c_related) for r in rs if p in products and r in products])

    # print("The number of nodes: ", len(c_product))
    # print("The number of edges: ", len(edge_set))

    with open('amazon_fashion_edges.p', 'wb') as f:
        pickle.dump(edge_set, f)
    with open('amazon_fashion_products.p', 'wb') as f:
        pickle.dump(products, f)

if __name__ == '__main__':
    main()

