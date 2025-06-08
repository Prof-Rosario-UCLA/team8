// Helper function to recursively convert date strings to Date objects in any nested structure.
export const parseDates = (data: any): any => {
  if (!data) return data;

  // Check if the string matches a common ISO 8601 format.
  if (typeof data === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(data)) {
    const date = new Date(data);
    // Ensure the parsed date is valid.
    if (!isNaN(date.getTime())) {
      return date;
    }
  }

  // If it's an array, recurse on each item.
  if (Array.isArray(data)) {
    return data.map(parseDates);
  }

  // If it's an object, recurse on each value.
  if (typeof data === 'object' && data !== null) {
    const newData: { [key: string]: any } = {};
    for (const key in data) {
      newData[key] = parseDates(data[key]);
    }
    return newData;
  }

  // Return the data unchanged if it's not a parsable string, array, or object.
  return data;
}; 