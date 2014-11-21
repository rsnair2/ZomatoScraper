<h1> Zomato Restaurant Parser </h1>

<a href="https://www.zomato.com"> Zomato </a> is a website dedicated to helping people discover great places to eat. As of writting this, it has 291,000 restaurants in around 15 countries listed. This is a 
web parser that can be used to mine data from the Zomato wesite about the restaurants. By default, the main function begins the process of mining for restaurants based 
on the specifed locations and saves the data to a file called zomato-json.db. 

The parse file contains the special purpose parsers that are used to extract information from the website. The default information that is mined comprises of:
	<ul>
		<li> title </li>
        <li> phone number </li>
        <li> address </li>
        <li> locality </li>
        <li> star ratings </li>
        <li> features </li>
        <li> cuisine </li>
        <li> price </li>
        <li> timings </li> 
        <li> whether cards are accepted </li>
        <li> menu - list of urls to the menu images </li>
    </ul>

***

&#169; Rajiv Nair (rsnair.me)