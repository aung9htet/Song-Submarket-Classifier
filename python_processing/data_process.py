import os
import pandas as pd
import lazypredict
import matplotlib.pyplot as plt
from lazypredict.Supervised import LazyClassifier
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import joblib
import numpy as np
from cyanite_api import CyaniteAPI
from spotify_api_intergration import SpotifyAPI

class ClassifyModel(object):

    def __init__(self):
        self.batch = "batch_2"
        self.processed_train_files = self.get_processed_train_files()
        self.processed_test_files = self.get_processed_test_files()
        self.spotify = SpotifyAPI()

    def get_processed_train_files(self):
        file = f"song_training_data_{self.batch}.csv"
        os.chdir('../processed_dataset')
        df = pd.read_csv(file)
        labels = list(df['label'])
        counter = {}
        for label in labels:
            if not label in counter:
                counter[label] = 0
            else:
                counter[label] += 1
        print(counter)
        df.fillna(0, inplace=True)
        # df = df.dropna(axis=1)
        return df
    
    def get_processed_test_files(self):
        file = f"song_test_data_{self.batch}.csv"
        os.chdir('../processed_dataset')
        df = pd.read_csv(file)
        labels = list(df['label'])
        counter = {}
        for label in labels:
            if not label in counter:
                counter[label] = 0
            else:
                counter[label] += 1
        print(counter)
        df.fillna(0, inplace=True)
        # df = df.dropna(axis=1)
        return df
    
    def test_model(self):
        x_train_data = self.processed_train_files.iloc[:, 1:]
        y_train_data = self.processed_train_files.iloc[:, 0:1]
        x_test_data = self.processed_test_files.iloc[:, 1:]
        y_test_data = self.processed_test_files.iloc[:, 0:1]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(x_train_data)
        X_test_scaled = scaler.transform(x_test_data)

        # Apply PCA
        pca = PCA(n_components=20)  # Adjust n_components or variance threshold as needed
        x_train_pca = pca.fit_transform(X_train_scaled)
        x_test_pca = pca.transform(X_test_scaled)

        # X_train, X_test, y_train, y_test = train_test_split(x_train_data, y_train_data,test_size=.5,random_state =123)
        clf = LazyClassifier(verbose=0,ignore_warnings=True, custom_metric=None)
        models,predictions = clf.fit(x_train_pca, x_test_pca, y_train_data, y_test_data)
        print(models)

    def pca_adjust_n_components(self):
        # Fit PCA on the standardized training data
        x_train_data = self.processed_train_files.iloc[:, 1:]
        pca = PCA().fit(x_train_data)

        # Plot cumulative explained variance
        plt.figure(figsize=(8, 6))
        plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_.cumsum(), marker='o', linestyle='--')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('Explained Variance by Number of Components')
        plt.show()

    def train_model(self):
        x_train_data = self.processed_train_files.iloc[:, 1:]
        y_train_data = self.processed_train_files.iloc[:, 0:1]
        x_test_data = self.processed_test_files.iloc[:, 1:]
        y_test_data = self.processed_test_files.iloc[:, 0:1]
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(x_train_data)
        X_test_scaled = scaler.transform(x_test_data)
        n_components = 20  
        pca = PCA(n_components=n_components)
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca = pca.transform(X_test_scaled)
        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train_pca, y_train_data)
        y_pred = rf_classifier.predict(X_test_pca)
        accuracy = accuracy_score(y_test_data, y_pred)
        print(f'Accuracy: {accuracy}')
        print('Classification Report:')
        print(classification_report(y_test_data, y_pred))
        joblib.dump(rf_classifier, 'random_forest_classifier.pkl')
        print('Trained Random Forest model saved as random_forest_classifier.pkl')
        joblib.dump(pca, 'pca_model.pkl')
        joblib.dump(scaler, 'scaler.pkl')
        print('PCA model saved as pca_model.pkl')
        print('Scaler saved as scaler.pkl')

    def get_song_data(self, track):
        feature = {}
        track = track[31:]
        track = self.spotify.get_track_data(track)['id']
        song_analyser = CyaniteAPI(track)
        try:
            mood, genre, advanced_genre, movement, character = song_analyser.get_data()
            feature = mood | genre | advanced_genre | movement | character
        except Exception as e:
            print(track)
            print(f"Failed to get song. Error: {e}")
        df = pd.DataFrame([feature])
        print(df)
        df.fillna(0, inplace=True)
        common_columns = df.columns.intersection(self.processed_train_files.columns)
        df = df[common_columns]
        return df

    def classify_model(self, track = "https://open.spotify.com/track/147gCksvDRmjG1pO51ZCcf?si=66182db9bdd34ef5"):
        rf_classifier = joblib.load('random_forest_classifier.pkl')
        pca = joblib.load('pca_model.pkl')
        scaler = joblib.load('scaler.pkl')

        feature = self.get_song_data(track)
        # Preprocess the new item
        new_item_scaled = scaler.transform(feature)
        new_item_pca = pca.transform(new_item_scaled)

        # Classify the new item
        prediction = rf_classifier.predict(new_item_pca)
        print(f'Predicted class: {prediction[0]}')

classify = ClassifyModel()
classify.train_model()
classify.classify_model()