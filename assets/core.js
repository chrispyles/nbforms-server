/**
	JavaScript for nbforms Config Generator
*/

var numQuestions = 1;
var questionOptions = {};
questionOptions[1] = 1;
var questionIsOption = {};
questionIsOption[1] = true;

// Function to change option inputs to placeholder input
function changeToPlaceholders(qNum) {
	if (questionIsOption[qNum]) {
		$('#q' + qNum + 'options').empty()
		var placeholderTemplate = `
			<div id="q` + qNum + `placeholder">
				<input type="text" name="questions[` + qNum + `][placeholder]" placeholder="Placeholder" id="q` + qNum + `p" class="col-md-12 form-control">
			</div>
		`;
		$(placeholderTemplate).appendTo('#q' + qNum + 'options');
		$('#addOption' + qNum).prop('disabled', true);
		questionIsOption[qNum] = false;
	}
}

// Function to change placeholder input to option inputs
function changeToOptions(qNum) {
	if (!questionIsOption[qNum]) {
		$('#q' + qNum + 'options').empty()
		questionOptions[qNum] = 0;
		addOption(qNum);
		$('#addOption' + qNum).prop('disabled', false);
		questionIsOption[qNum] = true;
	}
}

// Function to add an option to a question
function addOption(qNum) {
	questionOptions[qNum]++;
	var oNum = questionOptions[qNum];
	var optionTemplate = `
		<div class="row container" id="q` + qNum + `o` + oNum + `div">
			<input type="text" name="questions[` + qNum + `][options][]" placeholder="Option" id="q` + qNum + `o` + oNum + `" class="col-md-11 option form-control">
			<div class="align-content-center col-md-1">
				<button type="button"  class="delete-option btn btn-light align-content-center" onclick="deleteOption(` + qNum + `, ` + oNum + `)">X</button>
			</div>
		</div>
	`;
	$(optionTemplate).appendTo('#q' + qNum + 'options');
}

// Function to remove an option from a question
function deleteOption(qNum, oNum) {
	$('#q' + qNum + 'o' + oNum + 'div').remove()
}

// Function to add a question
function addQuestion() {
	numQuestions++;
	var qNum = numQuestions;
	questionIsOption[qNum] = true;
	questionOptions[qNum] = 1;
	var questionTemplate = `
		<div class="form-group col-md-6" id="q` + qNum + `div">

			<div class="row container">
			
				<div class="id-type-div">
					<input type="text" name="questions[` + qNum + `][identifier]" placeholder="Identifier" class="form-control col-md-6">

					<table><tr>
						<td colspan="2"><label for="questions[` + qNum + `][type]">Question Type</label></td>
					</tr><tr>
						<td><input type="radio" name="questions[` + qNum + `][type]" value="multiplechoice" class="option-types" onclick="changeToOptions(` + qNum + `)"> Multiple Choice</td>
						<td><input type="radio" name="questions[` + qNum + `][type]" value="checkbox" class="option-types" onclick="changeToOptions(` + qNum + `)"> Checkbox</td>
					</tr><tr>
						<td><input type="radio" name="questions[` + qNum + `][type]" value="text" class="placeholder-types" onclick="changeToPlaceholders(` + qNum + `)"> Text</td>
						<td><input type="radio" name="questions[` + qNum + `][type]" value="paragraph" class="placeholder-types" onclick="changeToPlaceholders(` + qNum + `)"> Paragraph</td>
					</tr></table>
				</div>

			</div>

			<textarea name="questions[` + qNum + `][question]" placeholder="Question" class="form-control question-input"></textarea>

			<div id="q` + qNum + `options">

				<div class="row container" id="q` + qNum + `o1div">
					<input type="text" name="questions[` + qNum + `][options][]" placeholder="Option" id="q` + qNum + `o1" class="col-md-11 option form-control">
					<div class="align-content-center col-md-1">
						<button type="button"  class="delete-option btn btn-light align-content-center" onclick="deleteOption(` + qNum + `, 1)">X</button>
					</div>
				</div>

			</div>

			<div class="row container justify-content-center question-buttons">

				<button type="button" class="btn btn-light add-option col-md-5" id="addOption` + qNum + `" onclick="addOption(` + qNum + `)">Add an Option</button>

				<button type="button" class="btn btn-light delete-question offset-md-1 col-md-5" onclick="deleteQuestion(` + qNum + `)">Delete Question</button>

			</div>

		</div>
	`
	$(questionTemplate).appendTo('#question-container')
}

// Function to delete a question
function deleteQuestion(qNum) {
	$('#q' + qNum + 'div').remove()
}

// Function to copy test output
function copyOutput() {
	var copyText = document.querySelector("#output-text");
	copyText.select();
	copyText.setSelectionRange(0, 99999);
	document.execCommand("copy");

	var copyButton = document.querySelector("#copy-button")
	copyButton.innerHTML = "Copied!";
}

// Function to download test file
function setupDownload(filename) {
	var text = document.querySelector("#output-text").value;
	var btn = document.querySelector("#download-btn");
	btn.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
	btn.setAttribute("download", filename)
}
