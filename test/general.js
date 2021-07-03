function readMore(moreID, buttonID) {
  var moreText = document.getElementById(moreID);
  var btnText = document.getElementById(buttonID);

  if (moreText.style.display === "inline") {
    btnText.innerHTML = "v"; 
	btnText.style.borderStyle = "none"
    moreText.style.display = "none";
  } else {
    btnText.innerHTML = "^"; 
	btnText.style.borderStyle = "solid none none none"
    moreText.style.display = "inline";
  }
}

let letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i","j","k", "l", "m","n","o","p","q","r","s"];

class ProblemGroup {
	// takes in list on inputs for each problem
	constructor(questions_id,answers_id, problemClass, inputs, single = false) {
		this.questions_id = questions_id;
		this.answers_id = answers_id;
		this.problemClass = problemClass;
		this.inputs = inputs;
		this.num_problems = inputs.length;
		//console.log(this.num_problems);
		this.single = single;
		this.problems = [];
		
		// get parent element
		let questions_elem = document.getElementById(this.questions_id);
		var i;
		for (i = 0; i < this.num_problems; i++) {
			let id = "sort" + String(i);
			
			var letter = document.createTextNode(letters[i] + ".");
			questions_elem.appendChild(letter)
			
			this.problems.push(new this.problemClass(this.inputs[i]))
		}
		//console.log(this.problems)
		this.refreshAll();
	}

	refreshAll() {
		// Clear question element
		let questions_elem = document.getElementById(this.questions_id);
		questions_elem.innerHTML = "";
		// Clear answers element
		let ans_elem = document.getElementById(this.answers_id);

		ans_elem.innerHTML = "";
		var i;
		for (i = 0; i < this.num_problems; i++) {
			this.problems[i].refresh()
			// Add question letter *if* it's not a "single" problem
			let letterBit
			if (!this.single) {
				letterBit = letters[i] + ".";
			} else {
				letterBit = "";
			}
			questions_elem.innerHTML += "<p>" + letterBit + this.problems[i].outString + "</p>";

		}
	}
	
	showAnswers() {
		// Clear answers element
		let ans_elem = document.getElementById(this.answers_id);
		//console.log(ans_elem)
		ans_elem.innerHTML = "";
		
		// Add answers subtitle
		var title = document.createElement("h4")
		title.innerText = "Answers"; 
		ans_elem.appendChild(title)
		
		// Print all problem answers
		var i;
		for (i = 0; i < this.num_problems; i++) {
			// Add answer
			
			// Add question letter *if* it's not a "single" problem
			let letterBit
			if (!this.single) {
				letterBit = letters[i] + ".";
			} else {
				letterBit = "";
			}
			
			ans_elem.innerHTML += "<p>" + letterBit + this.problems[i].answer + "</p>";
		}
	}
}


