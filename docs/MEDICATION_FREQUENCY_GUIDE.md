# Medication Frequency and Time Selection Guide

## Overview

The Electronic Medication Administration Record (eMAR) system now includes enhanced medication frequency and time selection features to provide more flexibility and usability for healthcare providers.

## Standard Medication Frequencies

The system supports the following standard medical abbreviations for medication frequencies:

### Common Frequencies

| Abbreviation | Full Name | Description | Times Per Day | Suggested Times |
|--------------|-----------|-------------|---------------|-----------------|
| **QD** | Once Daily | Once per day | 1 | 9:00 AM |
| **BID** | Twice Daily | Two times per day | 2 | 9:00 AM, 9:00 PM |
| **TID** | Three Times Daily | Three times per day | 3 | 9:00 AM, 1:00 PM, 9:00 PM |
| **QID** | Four Times Daily | Four times per day | 4 | 9:00 AM, 1:00 PM, 5:00 PM, 9:00 PM |

### Interval-Based Frequencies

| Abbreviation | Full Name | Description | Times Per Day | Suggested Times |
|--------------|-----------|-------------|---------------|-----------------|
| **Q4H** | Every 4 Hours | Six times per day | 6 | 12:00 AM, 4:00 AM, 8:00 AM, 12:00 PM, 4:00 PM, 8:00 PM |
| **Q6H** | Every 6 Hours | Four times per day | 4 | 12:00 AM, 6:00 AM, 12:00 PM, 6:00 PM |
| **Q8H** | Every 8 Hours | Three times per day | 3 | 6:00 AM, 2:00 PM, 10:00 PM |
| **Q12H** | Every 12 Hours | Twice per day | 2 | 8:00 AM, 8:00 PM |
| **Q24H** | Every 24 Hours | Once per day | 1 | 9:00 AM |

### Special Frequencies

| Abbreviation | Full Name | Description |
|--------------|-----------|-------------|
| **PRN** | As Needed | Administered as needed, no fixed schedule |
| **Custom** | Custom Frequency | User-defined frequency for non-standard schedules |

## Features

### 1. Frequency Selection Dropdown

When adding a new prescription, users can select from a dropdown menu containing all standard frequencies:

- **Clear Labels**: Each option shows both the abbreviation and full name (e.g., "BID (Twice Daily)")
- **Helpful Descriptions**: Below the dropdown, a hint text explains the frequency (e.g., "Two times per day")
- **Custom Option**: Select "Custom Frequency" to enter non-standard schedules

### 2. Auto-Suggested Administration Times

When a standard frequency is selected, the system automatically suggests appropriate administration times:

- **Smart Suggestions**: Times are calculated based on the frequency to ensure even distribution
- **One-Click Application**: Click the "✓ Use Suggested Times" button to automatically populate time slots
- **Visual Display**: Suggested times are shown clearly (e.g., "Suggested: 9:00 AM, 9:00 PM")

### 3. Extended Time Selection

Time slots now support 24-hour coverage:

- **All Hours Available**: Select any hour from 12:00 AM (Midnight) to 11:00 PM
- **Clear Formatting**: Times are displayed in both 12-hour and 24-hour formats
- **Flexible Management**: Add, remove, or modify time slots as needed

### 4. Custom Frequency Input

For non-standard medication schedules:

- **Free Text Entry**: Enter any custom frequency description
- **Examples Provided**: Placeholder text shows examples like "Every other day" or "Weekly on Monday"
- **Validation**: System validates format while allowing flexibility

## How to Use

### Adding a Prescription with Standard Frequency

1. Navigate to the **Prescriptions** tab in the Nurse Dashboard
2. Click **"+ Add Another Medicine"**
3. Fill in the basic information (Medicine Name, Dosage)
4. Select a frequency from the **Frequency** dropdown (e.g., "BID (Twice Daily)")
5. Review the suggested administration times displayed
6. Click **"✓ Use Suggested Times"** to apply them automatically
7. Adjust time slots if needed by selecting different times or adding/removing slots
8. Complete the rest of the form and submit

### Adding a Prescription with Custom Frequency

1. Navigate to the **Prescriptions** tab in the Nurse Dashboard
2. Click **"+ Add Another Medicine"**
3. Fill in the basic information (Medicine Name, Dosage)
4. Select **"Custom Frequency"** from the Frequency dropdown
5. Enter your custom frequency in the text field (e.g., "Every other day")
6. Manually add time slots using the **"+ Add Time"** button
7. Select appropriate times for each administration
8. Complete the rest of the form and submit

### Managing Time Slots

- **Add Time Slot**: Click the **"+ Add Time"** button to add a new time slot
- **Change Time**: Click on any time dropdown to select a different time
- **Remove Time Slot**: Click the **✕** button next to a time slot to remove it
- **Reorder**: Time slots are automatically sorted chronologically

## Best Practices

### Frequency Selection

1. **Use Standard Abbreviations**: When possible, use standard medical abbreviations (BID, TID, etc.) for consistency
2. **Be Specific**: For custom frequencies, provide clear, unambiguous descriptions
3. **Consider Patient Schedule**: Choose administration times that fit the patient's daily routine when possible

### Time Selection

1. **Even Distribution**: For multiple daily doses, space them evenly throughout the day
2. **Avoid Nighttime Doses**: Unless medically necessary, avoid scheduling doses during sleeping hours (typically 10 PM - 6 AM)
3. **Meal Considerations**: Consider whether medication should be taken with food when selecting times
4. **Use Suggested Times**: The system's suggested times are designed for optimal distribution and patient convenience

### Documentation

1. **Clear Instructions**: Ensure all frequency and timing information is clear and unambiguous
2. **Special Instructions**: Use the notes field for any special instructions (e.g., "Take with food")
3. **Review Before Submitting**: Always review the prescription preview before final submission

## API Integration

### Frequency Format

The API accepts frequency in two formats:

1. **Standard Abbreviations**: `BID`, `TID`, `QID`, `Q8H`, `Q12H`, `Q24H`, `PRN`, `QD`
2. **Custom Text**: Any descriptive text (e.g., "Three times daily", "Every other day")

### Time Slot Format

Time slots are comma-separated in 24-hour format:

```json
{
  "frequency": "BID",
  "time_slot": "09:00, 21:00"
}
```

### Example API Request

```json
POST /api/prescriptions
{
  "patient_id": "P001",
  "medicine_name": "Metformin",
  "dosage": "500mg",
  "frequency": "BID",
  "start_date": "2025-11-20",
  "end_date": "2025-12-20",
  "time_slot": "09:00, 21:00"
}
```

## Backward Compatibility

The enhanced system maintains full backward compatibility:

- **Existing Prescriptions**: All existing prescriptions continue to work without modification
- **Legacy Formats**: Text-based frequencies (e.g., "Twice daily") are still supported
- **Data Migration**: No data migration required

## Troubleshooting

### Issue: Suggested times don't match my needs

**Solution**: After using suggested times, you can modify them by clicking on each time dropdown and selecting different times.

### Issue: Need more time slots than suggested

**Solution**: Click the **"+ Add Time"** button to add additional time slots beyond the suggested ones.

### Issue: Custom frequency not saving

**Solution**: Ensure you've selected "Custom Frequency" from the dropdown before entering text in the custom field.

### Issue: Can't find a specific time

**Solution**: All times from 00:00 to 23:00 are available. Scroll through the dropdown to find the desired time.

## Support

For additional support or to report issues:

1. Check the [Architecture Guide](ARCHITECTURE.md) for system design details
2. Review the [API Documentation](../swagger.yaml) for API reference
3. Contact the development team through the project repository

## Future Enhancements

Planned improvements for future releases:

- Multi-day schedules (e.g., "Monday, Wednesday, Friday")
- Conditional frequencies (e.g., "PRN not to exceed 4 times daily")
- Integration with patient meal schedules
- Reminder notifications at administration times
- Analytics dashboard for frequency patterns

---

*Last Updated: November 2025*
*Version: 1.0*
