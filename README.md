# Set1: 
## Bug: 
+ **areEqual** function return false even 2 set are equal.
## Cannot test:
+ **unionOf** testing give a failed test, however unionOf test function use areEqual function so maybe unionOf function is right but test failed due to areEqual.

+ Same for **symmetricDifferenceOf** test function.

# Set2:
***Passed all test cases.***

# Set3:
## Bug:
+ **insertItem** function insert duplicated item.
+ **removeItem** return false when remove an item which is the set.
## Cannot test:
+ **areEqual** tesing give a failed test, however because insert and remove item work wrong so that test cases cannot response correctly.
+ Same for **symmetricDifferenceOf** test function.
+ Same for **unionOf** test function.(However unionOf edge cases testing - include at least 1 empty set works fine).

# Set4:
## Bug:
+ **symetricDifferenceOf** function works wrong for general cases. However edge cases testing - include at least 1 empty set passed the all the tests.

# Set5:
***Passed all test cases.***
