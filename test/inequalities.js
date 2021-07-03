//let letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i"];

class sortProblem {
  /* Number sorting problem
  
  */
  constructor(inputs) {
	// unpack inputs
	this.pos = inputs[0];
	this.neg = inputs[1]; 
	this.dec = inputs[2];
	this.frac = inputs[3]  

	this.refresh()
  }
  
  refresh() {
	this.strings = [];
	this.numbers = [];
	
	// positive numbers
	var i
	for (i = 0; i < this.pos; i++) {
		// Generate random number between 1 and 10
		this.numbers.push(1 + Math.floor(Math.random() * 10));
		this.strings.push(String(this.numbers.slice(-1)));
	}
	
	// negative numbers
	for (i = 0; i < this.neg; i++) {
		// Generate random number between 1 and 10
		this.numbers.push(-1 - Math.floor(Math.random() * 10));
		this.strings.push(String(this.numbers.slice(-1)));
	}
	
	// decimal number
	for (i = 0; i < this.dec; i++) {
		// Generate random number between 1 and 10
		var decnum = Math.random() * 5;
		var strNum = String(decnum).slice(0,3)
		
		if (decnum%1 === 0){
			decnum += 0.1
		}
		
		// 50% chance of being negative
		if (Math.random() > 0.5) {
			var sign = "-";
			decnum = - decnum;
		} else {
			var sign = "";
		}
		
		this.numbers.push(decnum)
		this.strings.push(sign + strNum);
	}
	// fractions
	for (i = 0; i < this.frac; i++) {
		// Denominator: Generate random int between 0 and 9
		let denom = Math.floor(2 + Math.random() * 7);
		// 25% chance of fraction being negative
		
		// Numerator: Generate random number between -4 and 4 time denominator
		let numerator = Math.floor(2 + 3*denom*Math.random());
		// if numer is multiple of denom, add one
		if (numerator % denom === 0 || denom % numerator === 0) {
			numerator += 1;
		}
		if (Math.random() > 0.75) {
			numerator = -numerator;
		}	
		
		// Put minus sign out the front
		if (numerator<0) {
			var sign = "-"
		} else {
			var sign = ""
		}
		
		this.numbers.push(numerator/denom)
		this.strings.push(sign + "\\frac{" + Math.abs(numerator) + "}{" + denom + "}");
	}
	
	//console.log(this.numbers)
	// Calculate answers (magic from internet)
	const keys = Array.from(this.numbers.keys()).sort((a, b) => this.numbers[a] - this.	numbers[b])
	let sortedStrings = keys.map(i => this.strings[i])
	this.answer = "$$".concat(sortedStrings.join(",\\; ")) + "$$";
	//console.log(this.answer)
	
	this.outString = "$$".concat(this.strings.join(",\\; ")) + "$$"
	}
}



const items = ["balls", "dice", "dogs", "students", "math problems", 
				"cats", "fish", "cars", "bikes", "players", "apples",
				"sandwiches", "hats", "doors", "clowns", "pens", "cups", 
				"ships", "pillows", "windows", "books", "zebras", 
				"potatoes", "stars"]
const eqSyms = [["=", "equal to"], 
				 ["\\ne", "not equal to" ], 
				 ["<", "less than"], 
				 [">", "greater than"],
				 ["\\ge", "greater than or equal to"],
				 ["\\le", "less than or equal to"]]
				 
class usingEqSyms {
  /* Using equality/inequality symbols
  
  */
  constructor() {
	//this.refresh();
  }
  
  refresh() {
	let symIndex = Math.floor(Math.random() * eqSyms.length);
	let itemIndex = Math.floor(Math.random() * items.length);
	let number = Math.floor(Math.random() * 35);
	
	  
	this.outString = ` The number of ${items[itemIndex]} (\$${items[itemIndex][0]}\$) is ${eqSyms[symIndex][1]} ${number}. `
	  
	
	this.answer = "$$" + `${items[itemIndex][0]} ${eqSyms[symIndex][0]} ${number}`+ "$$";
	
	//console.log(this.answer)
	}
}

function getSign(number) {
    if (number > 0) {
        return "+";
    } else if (number === 0) {
        return 0;
    } else if (number < 0) {
        return "-";
    }
    
}


class simpEqSyms {
  /* Using equality/inequality symbols
  
  Problem:
      A x + B ~ C x + D
  Answer:
      x ~ (D-B)/(A-C)
  
  */
  constructor(inputs) {
    this.prefA = inputs[0];
    this.prefB = inputs[1];
    this.prefC = inputs[2];
    this.prefD = inputs[3];
	this.refresh();
  }
  
  refresh() {
    // Generate random prefactors
	let A = Math.floor(1 + Math.random() * 5)*this.prefA;
	let B = Math.floor(5 - Math.random() * 10)*this.prefB;
	let C = Math.floor(5 - Math.random() * 10)*this.prefC;
	let D = Math.floor(5 - Math.random() * 10)*this.prefD;
	
	// Choose random inequality symbol
	let inequality = eqSyms[Math.floor(Math.random()*6)][0]
	
	// Make sure A and C aren't the same
	if (A === C) {
		A += 1;
	}
	
	// If we have only A and D, make sure A isn't 1 
	// (trivial problem e.g. simplify x ~ 5)
	if (B === 0 && C === 0 && A === 1) {
		A += Math.floor(Math.random()*3)
	}
	
	// Make sure D is non-zero (if D requested)
	if (D === 0 && this.prefD === 1) {
       D += 1;
	} 

	this.outString = "$$" 
	
	// First term
	if (this.prefA === 1) {
		// if coeff is -1 only writ	e minus sign
		if (A === -1) {
			this.outString += "-";
		// if coeff is not 1 then write ti
		} else if (A != 1) {
			this.outString += String(A);
		}
		this.outString += "x";
	}
	
	// Second term
	if (this.prefB && B != 0) {
       this.outString += getSign(B) + String(Math.abs(B));
	} 

	// inequality symbol
	this.outString += " " + inequality + " ";

	
	if (this.prefC && C != 0) {
		if (C === -1) {
			this.outString += "-" 
		} else if (C != 1) {
			this.outString += String(C)
		}
		this.outString += "x";
       //console.log("This printed")
	} 
	
	if (this.prefD && D != 0) {
		if (this.prefC === 1 || D < 0) {
			this.outString += getSign(D);
		}
        this.outString += String(Math.abs(D));
	} 
	this.outString += "$$";
	
	////// Calculate Answer ///////
	
	// reduce fraction
	let newFrac = reduceFraction(D - B, A - C);
	let numerator = newFrac[0];
	let denominator = newFrac[1];
	
	// Start answer string
	this.answer = "$$ x " + inequality + " ";
	
	if (denominator === 1) {
		this.answer += String(numerator);
	} else if (numerator === 0){
		this.answer += "0";
	} else {
		if (numerator < 0) {
			this.answer += "-";
		}
		this.answer += "\\frac{" + String(Math.abs(numerator)) + "}{" + String(denominator) + "}"
	}
	this.answer += "$$";
	}
}


