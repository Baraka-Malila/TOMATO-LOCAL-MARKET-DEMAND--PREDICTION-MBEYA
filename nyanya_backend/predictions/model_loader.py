"""
Tomato Model Loader for Colab-Generated Files
"""

import os
import pickle
import numpy as np


class TomatoModelLoader:
    """Loads Random Forest model from Colab .pkl files"""
    
    def __init__(self):
        self.model = None
        self.categorical_encoders = None
        self.target_encoder = None
        self.metadata = None
        self.is_trained = False
        
        self.models_dir = '/home/cyberpunk/LOCAL-MARKET-MBEYA-NYANYA/models'
        self.model_path = os.path.join(self.models_dir, 'rf_model.pkl')
        self.cat_encoders_path = os.path.join(self.models_dir, 'categorical_encoders.pkl')
        self.target_encoder_path = os.path.join(self.models_dir, 'target_encoder.pkl')
        self.metadata_path = os.path.join(self.models_dir, 'metadata.pkl')
        
        self.load_model()
    
    def load_model(self):
        """Load trained model and encoders from pickle files"""
        
        try:
            required_files = [self.model_path, self.cat_encoders_path, 
                            self.target_encoder_path, self.metadata_path]
            if not all(os.path.exists(path) for path in required_files):
                print("Model files not found")
                return False
            
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.cat_encoders_path, 'rb') as f:
                self.categorical_encoders = pickle.load(f)
            
            with open(self.target_encoder_path, 'rb') as f:
                self.target_encoder = pickle.load(f)
            
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            self.is_trained = True
            print("Model loaded successfully!")
            accuracy = self.metadata.get('accuracy', 0)
            print(f"Accuracy: {accuracy:.3f}")
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.is_trained = False
            return False
    
    def reload_model(self):
        """Reload model from files"""
        
        self.is_trained = False
        self.model = None
        self.categorical_encoders = None
        self.target_encoder = None
        self.metadata = None
        
        return self.load_model()
    
    def encode_features(self, rainfall_mm, temperature_c, market_day, school_open, 
                       disease_alert, last_week_demand, week, month):
        """Encode input features for prediction"""
        
        if not self.is_trained:
            raise ValueError("Model not loaded")
        
        try:
            last_week_encoded = self.categorical_encoders['Last_Week_Demand'].transform([last_week_demand])[0]
            month_encoded = self.categorical_encoders['Month'].transform([month])[0]
            
            market_day_int = 1 if market_day else 0
            school_open_int = 1 if school_open else 0
            disease_alert_int = 1 if disease_alert == 'Presence' else 0
            
            # Feature order: Rainfall_mm, Temperature_C, Market_Day, School_Open, 
            #                Disease_Alert, Last_Week_Demand, Month, Year
            features = np.array([[
                rainfall_mm,
                temperature_c,
                market_day_int,
                school_open_int,
                disease_alert_int,
                last_week_encoded,
                month_encoded,
                2024
            ]])
            
            return features
            
        except Exception as e:
            raise ValueError(f"Feature encoding failed: {str(e)}")
    
    def predict(self, rainfall_mm=75.0, temperature_c=22.0, market_day=True, 
                school_open=True, disease_alert='Absence', last_week_demand='Medium',
                week=1, month='January'):
        """Make demand prediction using trained model"""
        
        if not self.is_trained:
            raise ValueError("Model not loaded")
        
        try:
            features = self.encode_features(
                rainfall_mm, temperature_c, market_day, school_open,
                disease_alert, last_week_demand, week, month
            )
            
            prediction_encoded = self.model.predict(features)[0]
            prediction_proba = self.model.predict_proba(features)[0]
            confidence = np.max(prediction_proba)
            
            prediction = self.target_encoder.inverse_transform([prediction_encoded])[0]
            
            return prediction, confidence
            
        except Exception as e:
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def get_model_info(self):
        """Get model information"""
        
        if not self.is_trained:
            return {
                'is_trained': False,
                'message': 'Model not loaded'
            }
        
        return {
            'is_trained': True,
            'model_type': 'Random Forest Classifier',
            'accuracy': self.metadata.get('accuracy', 0),
            'training_date': self.metadata.get('training_date', 'Unknown'),
            'features': self.metadata.get('features', []),
            'target': self.metadata.get('target', 'Market_Demand')
        }


# Global model instance
predictor = TomatoModelLoader()

import os
import pickle
import numpy as np
from django.conf import settings


class TomatoModelLoader:
    """
    Loads and uses the saved Random Forest model for predictions.
    
    Model files are created in Google Colab and saved as:
    - rf_model.pkl (trained Random Forest model)
    - categorical_encoders.pkl (categorical feature encoders)
    - target_encoder.pkl (target variable encoder)
    - metadata.pkl (model metadata)
    """
    
    def __init__(self):
        self.model = None
        self.categorical_encoders = None
        self.target_encoder = None
        self.metadata = None
        self.is_trained = False
        
        # Model file paths
        self.models_dir = '/home/cyberpunk/LOCAL-MARKET-MBEYA-NYANYA/models'
        self.model_path = os.path.join(self.models_dir, 'rf_model.pkl')
        self.cat_encoders_path = os.path.join(self.models_dir, 'categorical_encoders.pkl')
        self.target_encoder_path = os.path.join(self.models_dir, 'target_encoder.pkl')
        self.metadata_path = os.path.join(self.models_dir, 'metadata.pkl')
        
        # Try to load model on initialization
        self.load_model()
    
    def load_model(self):
        """
        Load the trained model and encoders from pickle files.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            # Check if model files exist
            required_files = [self.model_path, self.cat_encoders_path, self.target_encoder_path, self.metadata_path]
            if not all(os.path.exists(path) for path in required_files):
                print("Model files not found. Train model in Google Colab first.")
                return False
            
            # Load model
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load categorical encoders
            with open(self.cat_encoders_path, 'rb') as f:
                self.categorical_encoders = pickle.load(f)
            
            # Load target encoder
            with open(self.target_encoder_path, 'rb') as f:
                self.target_encoder = pickle.load(f)
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            self.is_trained = True
            print("Model loaded successfully!")
            accuracy = self.metadata.get('accuracy', 0)
            print(f"Accuracy: {accuracy:.3f}")
            print(f"Training date: {self.metadata.get('training_date', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.is_trained = False
            return False
    
    def reload_model(self):
        """
        Reload the model from files (useful after updating model files).
        
        Returns:
            bool: True if model reloaded successfully, False otherwise
        """
        self.is_trained = False
        self.model = None
        self.categorical_encoders = None
        self.target_encoder = None
        self.metadata = None
        
        return self.load_model()
    
    def encode_features(self, rainfall_mm, temperature_c, market_day, school_open, 
                       disease_alert, last_week_demand, week, month):
        """
        Encode input features for prediction.
        
        Args:
            rainfall_mm (float): Rainfall in mm
            temperature_c (float): Temperature in Celsius
            market_day (bool): Is it a market day?
            school_open (bool): Are schools open?
            disease_alert (str): Disease status ('Presence'/'Absence')
            last_week_demand (str): Previous week demand ('Low'/'Medium'/'High')
            week (int): Week number
            month (str): Month name
        
        Returns:
            np.array: Encoded features ready for prediction
        """
        
        if not self.is_trained:
            raise ValueError("Model not loaded. Train model in Google Colab first.")
        
        try:
            # Encode categorical features - Note: Disease_Alert is not in encoders since it wasn't categorical in your data
            last_week_encoded = self.categorical_encoders['Last_Week_Demand'].transform([last_week_demand])[0]
            month_encoded = self.categorical_encoders['Month'].transform([month])[0]
            
            # Convert boolean to int
            market_day_int = 1 if market_day else 0
            school_open_int = 1 if school_open else 0
            
            # Convert disease_alert to int (since it wasn't encoded in Colab)
            disease_alert_int = 1 if disease_alert == 'Presence' else 0
            
            # Create feature array (must match training order from Colab)
            # Order: Rainfall_mm, Temperature_C, Market_Day, School_Open, Disease_Alert, Last_Week_Demand, Month, Year
            features = np.array([[
                rainfall_mm,             # Rainfall_mm
                temperature_c,           # Temperature_C
                market_day_int,          # Market_Day
                school_open_int,         # School_Open
                disease_alert_int,       # Disease_Alert (not encoded, just binary)
                last_week_encoded,       # Last_Week_Demand_encoded
                month_encoded,           # Month_encoded
                2024                     # Year (using 2024 as default)
            ]])
            
            return features
            
        except Exception as e:
            raise ValueError(f"Feature encoding failed: {str(e)}")
    
    def predict(self, rainfall_mm=75.0, temperature_c=22.0, market_day=True, 
                school_open=True, disease_alert='Absence', last_week_demand='Medium',
                week=1, month='January'):
        """
        Make demand prediction using the trained model.
        
        Args:
            rainfall_mm (float): Expected rainfall
            temperature_c (float): Expected temperature
            market_day (bool): Is it a market day?
            school_open (bool): Are schools open?
            disease_alert (str): Disease status
            last_week_demand (str): Previous week demand
            week (int): Week number
            month (str): Month name
        
        Returns:
            tuple: (predicted_demand, confidence_score)
        """
        
        if not self.is_trained:
            raise ValueError("Model not loaded. Train model in Google Colab first.")
        
        try:
            # Encode features
            features = self.encode_features(
                rainfall_mm, temperature_c, market_day, school_open,
                disease_alert, last_week_demand, week, month
            )
            
            # Make prediction
            prediction_encoded = self.model.predict(features)[0]
            prediction_proba = self.model.predict_proba(features)[0]
            confidence = np.max(prediction_proba)
            
            # Decode prediction back to original labels
            prediction = self.target_encoder.inverse_transform([prediction_encoded])[0]
            
            return prediction, confidence
            
        except Exception as e:
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def get_model_info(self):
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information including accuracy, training date, etc.
        """
        if not self.is_trained:
            return {
                'is_trained': False,
                'message': 'Model not loaded. Train in Google Colab first.'
            }
        
        return {
            'is_trained': True,
            'model_type': 'Random Forest Classifier',
            'accuracy': self.metadata.get('accuracy', 0),
            'training_date': self.metadata.get('training_date', 'Unknown'),
            'features': self.metadata.get('features', []),
            'target': self.metadata.get('target', 'Market_Demand')
        }


# Global model instance
predictor = TomatoModelLoader()
