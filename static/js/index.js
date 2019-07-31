
selected_books = {}
selected_chapters = []

function selectBook() {
    i = document.getElementById("books").value
    tag = document.getElementById("book_" + i)
    selected_books[i] = tag.innerHTML
    //tag.outerHTML = ""
    books_res = document.getElementById("books_res")
    books_res.innerHTML = ""
    for(k in selected_books){
	btn = document.createElement('button')
	btn.innerHTML = selected_books[k]
	btn.onclick = function(j){
	    return function(){
		unselectBook(j)
	    }
	}(k)
	btn.id = "book_btn_" + k
	books_res.appendChild(btn)
    }
}

function unselectBook(i) {
    delete selected_books[i]
    document.getElementById("book_btn_" + i).outerHTML = ""
}

function selectChapter() {
    book_i = document.getElementById("books").value
    book_name = document.getElementById("book_" + book_i).innerHTML
    chapter = document.getElementById("chapters").value
    selected_chapters.push([book_i, chapter])
    root = document.getElementById("chapters_res")
    root.innerHTML = ""
    for(var j = 0; j < selected_chapters.length; j++){
	k = selected_chapters[j]
	btn = document.createElement('button')
	book_name = document.getElementById("book_" + k[0]).innerHTML
	btn.innerHTML = book_name + ":" + k[1]
	btn.onclick = function(index){
	    return function(){
		unselectChapter(index)
	    }
	}(k)
	btn.id = "chapter_btn_" + k[0] + "_" + k[1]
	root.appendChild(btn)
    }
}

function unselectChapter(index) {
    selected_chapters.pop(index)
    document.getElementById("chapter_btn_" + index[0] + "_" + index[1]).outerHTML = ""
}

function go() {
    var left = document.getElementById("left").value
    var right = document.getElementById("right").value
    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if(req.readyState === XMLHttpRequest.DONE && req.status === 200) {
	    var link = document.getElementById("download_link")
            link.href="/res/" + JSON.parse(req.response).res + ".epub"
	    link.innerHTML = "Download link"
	    link.click()
        };
    };
    req.open("GET", "/generate?left=" + left + "&right=" + right);
    req.send();
    
}


function load() {
    var req = new XMLHttpRequest();
    req.onreadystatechange = function () {
        if(req.readyState === XMLHttpRequest.DONE && req.status === 200) {
            modules = JSON.parse(req.response).modules
            left = document.getElementById("left")
	    right = document.getElementById("right")
            for(i=0; i<modules.length; i++){
                o = document.createElement('option')
                o.text = modules[i]
                o.value = modules[i]
                left.appendChild(o)
		right.appendChild(o.cloneNode(true))
            }
	    
        };
    };
    req.open("GET", "/modules");
    req.send();
}
