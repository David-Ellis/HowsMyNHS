//console.log("Loaded myMath.js")

function findMatchingItems(arr1, arr2) {
	// Finds matching items in two arrays
	let outArr = [];
	for (var i in arr1) {
		if (arr2.indexOf(arr1[i]) != -1){
			outArr.push(arr1[i])
		}
	}
	return outArr
}

function findFactors(number) {
	// find factors for a give number
	
	//sign doesn't matter
	number = Math.abs(number)
	if (number === 1) {
		return [1];
	} else {
		let factors = [];
		for (i = 1; i <= Math.ceil(number/2); i++){
			if (number % i === 0) {
				factors.push(i);
			}
		}
		
		// Add the number itself
		factors.push(number)
		
		return factors.sort()
	}
}

function lcf(number1, number2) {
	// Find largest common factor of given pair of numbers
	
	// find factors
	let factors1 = findFactors(number1);
	let factors2 = findFactors(number2);
	
	// common factors
	let commonFactors = findMatchingItems(factors1, factors2)
	
	// return largest
	return Math.max(...commonFactors)
}

function reduceFraction(numerator, denominator) {
	let factor = lcf(numerator, denominator)
	numerator = numerator/factor;
	denominator = denominator/factor;
	
	//// deal with negatives ////
	
	// Both -ve => return both +ve
	if (numerator < 0 && denominator < 0) {
		numerator = Math.abs(numerator);
		denominator = Math.abs(denominator);
	// One -ve => return -ve on the numerator
	} else if (numerator < 0 || denominator < 0) {
		numerator = -Math.abs(numerator);
		denominator = Math.abs(denominator);
	}
	
	return [numerator, denominator]
}

function fractionString(num, den) {
	
	// reduce fraction
	let newFrac = reduceFraction(num, den);
	num = newFrac[0];
	den = newFrac[1];

	// Deal with possible whole numbers
	if (den === 0) {
		return `Error: Zero denominator given.`;
	} else if (num === 0) {
		return "0";
	} else if (den === 1) {
		return String(num);
	}
	let sign = "";
	
	// get sign
	if ( ((num>0)&(den<0)) || ((num<0)&(den>0))) {
		sign = "-";
	}
	num = Math.abs(num);
	den = Math.abs(den);
	
	return sign + "\\frac{" + String(num) + "}{" + String(den) + "}";
}