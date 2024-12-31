def quicksort(arr):
    """
    This function implements the QuickSort algorithm to sort an array in-place.
    
    The algorithm works by:
    1. Selecting a 'pivot' element from the array.
    2. Partitioning the other elements into two sub-arrays, according to whether they are less than or greater than the pivot.
    3. Recursively sorting the sub-arrays.
    
    Here's a breakdown of the implementation:
    """
    if len(arr) <= 1:  # Base case: if the array has 1 or fewer elements, it's already sorted
        return arr
    
    else:
        # Choose the middle element as the pivot. This choice helps to avoid worst-case scenarios for already sorted arrays
        pivot = arr[len(arr) // 2]
        
        # List comprehension to create sublists:
        # - 'left' contains all elements less than the pivot
        left = [x for x in arr if x < pivot]
        
        # - 'middle' contains all elements equal to the pivot
        middle = [x for x in arr if x == pivot]
        
        # - 'right' contains all elements greater than the pivot
        right = [x for x in arr if x > pivot]
        
        # Recursively sort 'left' and 'right', then concatenate with 'middle'
        return quicksort(left) + middle + quicksort(right)
