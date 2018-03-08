// js script to fetch IPs of DA's
// https://metrics.torproject.org/rs.html#search/flag:authority
var table = document.querySelector('#torstatus_results');
var removeTh = 1;
var trs = Array.prototype.slice.call(table.querySelectorAll('tr'), removeTh);
trs.map(item => item.children[5].innerHTML);

// fot potential extensions
// fetch('https://metrics.torproject.org/rs.html#search/flag:authority')
// .then(response => response.text())
// .then(page => console.log(page.slice(0, 100)))

// rewrite in python, with periodic list updates?