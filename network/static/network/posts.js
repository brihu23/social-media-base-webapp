document.addEventListener('DOMContentLoaded', function() {

	main();

	
	function main ()
	{
		edit();
		likes();
		follow();
	}
	

	function follow(){
		console.log("follow is running")
		if (document.querySelector("#followbtn") === null){

		} else {
			document.querySelector("#followbtn").addEventListener('click', function(){

				ptof = this.getAttribute("data-number")
				console.log(ptof)
				token = document.querySelector("#token").getAttribute('data-token');
	            console.log("token:" + token)
	            followspan = document.querySelector("#numfollow")

				fetch(`/follow`, {
					method: 'PUT',
					body: JSON.stringify({
						"ptof": ptof,
					}),
					headers: {"X-CSRFToken": token},
				})
				.then(response => response.json())
				.then(result => {

					console.log(result)

					if (result["message"] === "own"){
							alert("You can't like your own posts")
						} else if (result["message"] === "unfollowed") {
							this.innerHTML = "follow"
							followspan.innerHTML = `Followers: ${result["numfoll"]}`

						} else {
							this.innerHTML= "Un-Follow"
							followspan.innerHTML = `Followers: ${result["numfoll"]}`
						}

				})
			})

		}
	}

	function edit(){
		console.log("edit is running")
		document.querySelectorAll('.edit').forEach(function(button) {
			button.onclick = function() {

				console.log(this.parentNode.parentNode.firstChild.innerHTML)

				content = getSibling(this.parentNode, "content")

				console.log(content)


				form = `<form> <textarea id = "edit-content" class = "form-control"> ${content.innerHTML} </textarea>
				 <button id = "edit-button" class="btn btn-primary"> Done! </button> </form>`

				content.innerHTML = form
				disable("edit", true)
				

				document.querySelector("#edit-button").addEventListener('click', function(event){
					event.preventDefault();

					newContent = document.querySelector("#edit-content").value
					post_id = content.getAttribute('data-number')	
					console.log("post_id" + post_id)				
					token = document.querySelector("#token").getAttribute('data-token');

					fetch('/post', {
						method: 'PUT',
						body: JSON.stringify({
							"post_id": post_id,
							"newContent": newContent
						}),
						headers: {"X-CSRFToken": token},
					})

					.then(response => response.json())
					.then(result => {
						console.log(result)
						content.innerHTML = newContent
					})

					disable("edit", false)


				})

		
			}

		})

	}



	function likes(){
		console.log("likes is running")

		document.querySelectorAll('.likes').forEach(function(emoticon) {


			emoticon.onclick = function() {

				parent = this.parentElement
				//console.log("this: " + parent)
				id = this.getAttribute('data-number');
				console.log("id: "+ id);

				if (document.querySelector('#userprof') === null) {
					location.replace("/login")
					
				}
				liker = document.querySelector('#userprof').innerHTML
				//console.log("liker: " + liker);

                token = document.querySelector("#token").getAttribute('data-token');
                console.log("token:" + token)
			
				fetch(`/like/${id}`, {

					method: 'PUT',
					body: JSON.stringify({
						liker: liker,
					}),
					headers: { "X-CSRFToken": token },

				})
				.then(response => response.json())
				.then(result => {
					console.log(this)
					likes = document.querySelector("#likes")
					console.log(result['likes'])
					console.log(parent.childNodes[2])


					if (result["message"] === "own"){
						alert("You can't like your own posts")
					} else if (result["message"] === "unlike") {
						parent.childNodes[1].innerHTML = result["likes"]
						this.style.backgroundColor ="lightgrey"
					} else {
						parent.childNodes[1].innerHTML = result["likes"]
						this.style.backgroundColor =  "lightblue"
					}
					
				})
				
			}
		})
		
	}

	
})


	function getSibling(node, classname){
		var wantedsibling;
		sibling = node.parentNode.firstChild
		while (sibling) {
			
			if (sibling.classList){
				if(sibling.classList.contains(classname)){
				wantedsibling = sibling;
				}
			}
			sibling = sibling.nextSibling;
		}

		return wantedsibling;
	}


	function disable(classname, start){
		document.querySelectorAll('.'+ classname).forEach(function(object) {
			if (start) {
				object.disabled = true;
			} else {
				object.disabled = false;
			}
		})

	}



