import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# 1. Access the excel data

df = pd.read_excel("g6_research_data.xlsx")

df.loc[df['Flip_Count'] >= 1, 'Stock'] = 1

x = df['Generic_ID'].to_numpy() # Generic player names to make it easier to loop through
y = df['Flip_Count'].to_numpy() # Binary values if they transferred >= 1 time 


# 2. Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(x, y, train_size=0.2, random_state=42)

# 3. Initialize and train the model
model = LogisticRegression()
model.fit(X_train, y_train)

# 4. Make predictions
predictions = model.predict(X_test)

# 5. Evaluate the model
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy * 100}%")
print("\nClassification Report:\n", classification_report(y_test, predictions))