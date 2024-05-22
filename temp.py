''' @app.route('/area_position', methods=['GET'])
def area_position():
    # Fetch linked areas and positions from area_position table
    area_positions = areaposition.query.all()
    print(area_positions)

    # Render the template with linked areas and positions
    return render_template('area_position.html', area_positions=area_positions) '''

'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Area and Position Dropdowns</title>
</head>
<body>
    <h1>Select Area and Position</h1>
    <form>
        <label for="area">Select Area:</label>
        <select id="area" name="area">
            <option value="">Select Area</option>
            {% for area_position in area_positions %}
                <option value="{{ area_position.area_id }}">{{ area_position.area.area_name }}</option>
            {% endfor %}
        </select>
        <br><br>
        <label for="position">Select Position:</label>
        <select id="position" name="position">
            <option value="">Select Position</option>
            {% for area_position in area_positions %}
                <option value="{{ area_position.position_id }}">{{ area_position.position.position_name }}</option>
            {% endfor %}
        </select>
        <br><br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
'''