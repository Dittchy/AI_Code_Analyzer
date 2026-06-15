def findsecondlargest(nums):
    if len(nums)< 2:
        return None
    largest = second = float('-inf')
    
    for num in nums:
        if num > largest:
            second = largest
            largest = num
        elif num > second and num!= largest:
            second = num
    return second
      
    
print(findsecondlargest([3, 1, 4, 1, 5, 9]))