from flask import Flask, render_template, request, jsonify
import numpy as np
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)


FOOD_DATABASE = {
    # Roti & Bread
    'roti': {'name': 'Roti (1 medium)', 'serving': '1 piece', 'calories': 120, 'protein_g': 3, 'carbs_g': 18, 'fat_g': 3.7},
    'chapati': {'name': 'Chapati (1 medium)', 'serving': '1 piece', 'calories': 120, 'protein_g': 3, 'carbs_g': 18, 'fat_g': 3.7},
    'paratha': {'name': 'Paratha (1 medium)', 'serving': '1 piece', 'calories': 200, 'protein_g': 4, 'carbs_g': 24, 'fat_g': 10},
    'naan': {'name': 'Naan (1 piece)', 'serving': '1 piece', 'calories': 262, 'protein_g': 7, 'carbs_g': 45, 'fat_g': 5},
    
    # Rice
    'rice': {'name': 'White Rice', 'serving': '100g', 'calories': 130, 'protein_g': 2.7, 'carbs_g': 28, 'fat_g': 0.3},
    'brown rice': {'name': 'Brown Rice', 'serving': '100g', 'calories': 111, 'protein_g': 2.6, 'carbs_g': 23, 'fat_g': 0.9},
    'biryani': {'name': 'Biryani', 'serving': '100g', 'calories': 170, 'protein_g': 5, 'carbs_g': 25, 'fat_g': 5},
    
    # Daal/Lentils
    'daal': {'name': 'Daal (cooked)', 'serving': '100g', 'calories': 116, 'protein_g': 9, 'carbs_g': 20, 'fat_g': 0.4},
    'dal': {'name': 'Dal (cooked)', 'serving': '100g', 'calories': 116, 'protein_g': 9, 'carbs_g': 20, 'fat_g': 0.4},
    'rajma': {'name': 'Rajma (kidney beans)', 'serving': '100g', 'calories': 127, 'protein_g': 8.7, 'carbs_g': 23, 'fat_g': 0.5},
    'chana': {'name': 'Chana (chickpeas)', 'serving': '100g', 'calories': 164, 'protein_g': 8.9, 'carbs_g': 27, 'fat_g': 2.6},
    
    # Protein Sources
    'chicken': {'name': 'Chicken Breast', 'serving': '100g', 'calories': 165, 'protein_g': 31, 'carbs_g': 0, 'fat_g': 3.6},
    'chicken breast': {'name': 'Chicken Breast', 'serving': '100g', 'calories': 165, 'protein_g': 31, 'carbs_g': 0, 'fat_g': 3.6},
    'egg': {'name': 'Egg (1 large)', 'serving': '1 piece', 'calories': 78, 'protein_g': 6.3, 'carbs_g': 0.6, 'fat_g': 5.3},
    'eggs': {'name': 'Egg (1 large)', 'serving': '1 piece', 'calories': 78, 'protein_g': 6.3, 'carbs_g': 0.6, 'fat_g': 5.3},
    'paneer': {'name': 'Paneer', 'serving': '100g', 'calories': 265, 'protein_g': 18, 'carbs_g': 1.2, 'fat_g': 20.8},
    'fish': {'name': 'Fish', 'serving': '100g', 'calories': 206, 'protein_g': 22, 'carbs_g': 0, 'fat_g': 12},
    'mutton': {'name': 'Mutton', 'serving': '100g', 'calories': 294, 'protein_g': 25, 'carbs_g': 0, 'fat_g': 21},
    
    # Dairy
    'milk': {'name': 'Milk (full fat)', 'serving': '100ml', 'calories': 61, 'protein_g': 3.2, 'carbs_g': 4.8, 'fat_g': 3.3},
    'curd': {'name': 'Curd/Dahi', 'serving': '100g', 'calories': 60, 'protein_g': 3.5, 'carbs_g': 4.7, 'fat_g': 3.3},
    'dahi': {'name': 'Dahi/Curd', 'serving': '100g', 'calories': 60, 'protein_g': 3.5, 'carbs_g': 4.7, 'fat_g': 3.3},
    'yogurt': {'name': 'Yogurt', 'serving': '100g', 'calories': 59, 'protein_g': 10, 'carbs_g': 3.6, 'fat_g': 0.4},
    
    # Vegetables
    'potato': {'name': 'Potato', 'serving': '100g', 'calories': 77, 'protein_g': 2, 'carbs_g': 17, 'fat_g': 0.1},
    'aloo': {'name': 'Aloo (potato)', 'serving': '100g', 'calories': 77, 'protein_g': 2, 'carbs_g': 17, 'fat_g': 0.1},
    'tomato': {'name': 'Tomato', 'serving': '100g', 'calories': 18, 'protein_g': 0.9, 'carbs_g': 3.9, 'fat_g': 0.2},
    'onion': {'name': 'Onion', 'serving': '100g', 'calories': 40, 'protein_g': 1.1, 'carbs_g': 9.3, 'fat_g': 0.1},
    
    # Fruits
    'apple': {'name': 'Apple (1 medium)', 'serving': '1 piece', 'calories': 95, 'protein_g': 0.5, 'carbs_g': 25, 'fat_g': 0.3},
    'banana': {'name': 'Banana (1 medium)', 'serving': '1 piece', 'calories': 105, 'protein_g': 1.3, 'carbs_g': 27, 'fat_g': 0.4},
    'orange': {'name': 'Orange (1 medium)', 'serving': '1 piece', 'calories': 62, 'protein_g': 1.2, 'carbs_g': 15, 'fat_g': 0.2},
    
    # Snacks
    'samosa': {'name': 'Samosa (1 piece)', 'serving': '1 piece', 'calories': 262, 'protein_g': 4, 'carbs_g': 30, 'fat_g': 13},
    'pakora': {'name': 'Pakora (100g)', 'serving': '100g', 'calories': 230, 'protein_g': 4, 'carbs_g': 25, 'fat_g': 12},
    'biscuit': {'name': 'Biscuit (1 piece)', 'serving': '1 piece', 'calories': 47, 'protein_g': 0.6, 'carbs_g': 7, 'fat_g': 1.8},
    
    # Sweets
    'gulab jamun': {'name': 'Gulab Jamun (1 piece)', 'serving': '1 piece', 'calories': 175, 'protein_g': 2, 'carbs_g': 25, 'fat_g': 8},
    'jalebi': {'name': 'Jalebi (100g)', 'serving': '100g', 'calories': 458, 'protein_g': 1, 'carbs_g': 68, 'fat_g': 20},
    'ladoo': {'name': 'Ladoo (1 piece)', 'serving': '1 piece', 'calories': 180, 'protein_g': 3, 'carbs_g': 23, 'fat_g': 9},
}

# Session storage
meal_history = []

def parse_food_query(query):
    """
    Parse natural language food query
    Example: "2 roti, 100g chicken, 1 apple" 
    Returns: list of {food, quantity, unit}
    """
    query = query.lower().strip()
    items = [item.strip() for item in query.split(',')]
    
    parsed_items = []
    for item in items:
        words = item.split()
        quantity = 1  # default
        food_name = item
        
        if words and words[0].replace('.', '').isdigit():
            quantity = float(words[0])
            food_name = ' '.join(words[1:])
        
        food_name = food_name.replace('g', '').replace('grams', '').replace('cup', '').replace('piece', '').replace('pieces', '').strip()
        
        parsed_items.append({
            'quantity': quantity,
            'food': food_name
        })
    
    return parsed_items

def get_nutrition_data(food_query):
    """
    Get nutrition from local database (NO API NEEDED!)
    Args: food_query (str) - e.g., "2 roti, 100g chicken"
    Returns: dict with nutrition data
    """
    try:
        parsed_items = parse_food_query(food_query)
        nutrition_data = []
        
        for item in parsed_items:
            food_name = item['food']
            quantity = item['quantity']
            
            found = False
            for key, data in FOOD_DATABASE.items():
                if key in food_name or food_name in key:

                    nutrition = {
                        'name': f"{quantity} x {data['name']}",
                        'calories': data['calories'] * quantity,
                        'protein_g': data['protein_g'] * quantity,
                        'carbohydrates_total_g': data['carbs_g'] * quantity,
                        'fat_total_g': data['fat_g'] * quantity
                    }
                    nutrition_data.append(nutrition)
                    found = True
                    break
            
            if not found:
                nutrition_data.append({
                    'name': f"{quantity} x {food_name} (Not in database)",
                    'calories': 0,
                    'protein_g': 0,
                    'carbohydrates_total_g': 0,
                    'fat_total_g': 0
                })
        
        if nutrition_data:
            return {'success': True, 'data': nutrition_data}
        else:
            return {'success': False, 'error': 'No food items recognized'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_nutrition_totals(nutrition_data):
    """Calculate totals using NumPy"""
    if not nutrition_data:
        return None
    
    def safe_float(value):
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    calories = np.array([safe_float(item.get('calories', 0)) for item in nutrition_data], dtype=np.float64)
    protein = np.array([safe_float(item.get('protein_g', 0)) for item in nutrition_data], dtype=np.float64)
    carbs = np.array([safe_float(item.get('carbohydrates_total_g', 0)) for item in nutrition_data], dtype=np.float64)
    fat = np.array([safe_float(item.get('fat_total_g', 0)) for item in nutrition_data], dtype=np.float64)
    
    total_calories = float(np.sum(calories))
    total_protein = float(np.sum(protein))
    total_carbs = float(np.sum(carbs))
    total_fat = float(np.sum(fat))
    
    total_macros = total_protein * 4 + total_carbs * 4 + total_fat * 9
    
    if total_macros > 0:
        protein_percent = (total_protein * 4 / total_macros) * 100
        carbs_percent = (total_carbs * 4 / total_macros) * 100
        fat_percent = (total_fat * 9 / total_macros) * 100
    else:
        protein_percent = carbs_percent = fat_percent = 0
    
    return {
        'total_calories': round(total_calories, 1),
        'total_protein': round(total_protein, 1),
        'total_carbs': round(total_carbs, 1),
        'total_fat': round(total_fat, 1),
        'protein_percent': round(protein_percent, 1),
        'carbs_percent': round(carbs_percent, 1),
        'fat_percent': round(fat_percent, 1),
        'items': nutrition_data
    }

def calculate_daily_stats():
    """Calculate daily statistics"""
    if not meal_history:
        return None
    
    all_calories = np.array([float(meal['totals']['total_calories']) for meal in meal_history], dtype=np.float64)
    all_protein = np.array([float(meal['totals']['total_protein']) for meal in meal_history], dtype=np.float64)
    
    return {
        'total_meals': len(meal_history),
        'total_calories_today': float(np.sum(all_calories)),
        'total_protein_today': float(np.sum(all_protein)),
        'avg_calories_per_meal': float(np.mean(all_calories)),
        'max_calories_meal': float(np.max(all_calories))
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_food():
    try:
        data = request.get_json()
        food_query = data.get('food_query', '').strip()
        meal_type = data.get('meal_type', 'Snack')
        
        if not food_query:
            return jsonify({'success': False, 'error': 'Please enter food items'})
        
        # Get nutrition from local database
        result = get_nutrition_data(food_query)
        
        if not result['success']:
            return jsonify(result)
        
        totals = calculate_nutrition_totals(result['data'])
        
        if not totals:
            return jsonify({'success': False, 'error': 'Unable to calculate nutrition'})
        
        meal_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'meal_type': meal_type,
            'food_query': food_query,
            'totals': totals
        }
        meal_history.append(meal_entry)
        
        daily_stats = calculate_daily_stats()
        
        return jsonify({
            'success': True,
            'meal': meal_entry,
            'daily_stats': daily_stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history', methods=['GET'])
def get_history():
    daily_stats = calculate_daily_stats()
    return jsonify({
        'success': True,
        'history': meal_history,
        'daily_stats': daily_stats
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    global meal_history
    meal_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/export', methods=['GET'])
@app.route('/api/export', methods=['GET'])
def export_data():
    """Export meal history as CSV"""
    try:
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'Timestamp', 
            'Meal Type', 
            'Food Items', 
            'Total Calories (kcal)', 
            'Protein (g)', 
            'Carbs (g)', 
            'Fat (g)',
            'Protein %',
            'Carbs %',
            'Fat %'
        ])
        
        for meal in meal_history:
            writer.writerow([
                meal['timestamp'],
                meal['meal_type'],
                meal['food_query'],
                meal['totals']['total_calories'],
                meal['totals']['total_protein'],
                meal['totals']['total_carbs'],
                meal['totals']['total_fat'],
                meal['totals']['protein_percent'],
                meal['totals']['carbs_percent'],
                meal['totals']['fat_percent']
            ])

        if meal_history:
            daily_stats = calculate_daily_stats()
            writer.writerow([])  # Empty row
            writer.writerow(['DAILY SUMMARY', '', '', '', '', '', '', '', '', ''])
            writer.writerow([
                'Total Meals', 
                daily_stats['total_meals'],
                '',
                daily_stats['total_calories_today'],
                daily_stats['total_protein_today'],
                '',
                '',
                '',
                '',
                ''
            ])
        
        csv_string = output.getvalue()
        output.close()
        
        from flask import make_response
        response = make_response(csv_string)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=nutrition-log-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/foods', methods=['GET'])
def get_food_list():
    """Get list of available foods"""
    foods = [{'key': k, 'name': v['name'], 'serving': v['serving']} for k, v in FOOD_DATABASE.items()]
    return jsonify({'success': True, 'foods': foods})

if __name__ == '__main__':
    app.run(debug=True, port=5000)



#Author---->Raghaw Shukla
