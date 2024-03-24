## Comparison of Relational Databases vs NoSql Databases 
### Relational Databases
#### Strengths:
-  **Structured Data Modeling**: Relational databases are ideal for applications where data is well-structured and standardized. They use tables, relationships, and SQL for querying and manipulating data.
	
		Your data is still a work in progress -> not well-structured and standardized
	
-  **Powerful Querying Capabilities**: SQL provides a powerful query language allowing complex queries and aggregations.
-  (**Transaction Consistency**: Relational databases offer ACID properties (Atomicity, Consistency, Isolation, Durability), ensuring transactions are reliably and consistently executed.)
			
			Not important for your project, we don´t have a lot of reading 
		and writing operations in parallel (transactional).
#### Weaknesses:
-  **Rigid Schema**: Relational databases require a fixed schema, meaning changes to the data structure are often cumbersome and may impact existing data if the schema changes.
			
			Our data may change during the project development -> problems see above
-  **Complexity with Hierarchical Data**: If your data is hierarchical or heavily nested, modeling and querying in relational databases can become complex.

		For example we can´t save your data on job skills as a list in a field, 
		we would have to create a new table for this. 
		This is more complicated, however it would save storage space because of avoiding redundance.
-  **Scalability**: Traditional relational databases may struggle with horizontal scaling across multiple servers, although it's possible with technologies like sharding and replication. 

			Not very likely our project will reach the state where this becomes a major concern, 
			however if it would continue running it could be a future problem.
### NoSQL Databases
### Strengths

-  **Flexible Data Model**: NoSQL databases offer a more flexible data model, allowing storage of various types of data without requiring a fixed schema. This enables easier scalability and adaptation to changing requirements.
-  **Scalability**: Many NoSQL databases are optimized for horizontal scaling, making them well-suited for handling large volumes of data distributed across multiple servers.

		See weaknesses of SQL databases 
-  **Performance with Large Data**: NoSQL databases can often scale better and provide higher performance with large datasets compared to relational databases.

		Again, your project will probably not reach this size.
-  **Diverse Data Types**: NoSQL databases often support a variety of data types, including structured, unstructured, and semi-structured data.

		This is good to have the choice and not be limited ...

### Weaknesses

-  **Consistency Model**: Some NoSQL databases prioritize availability and partition tolerance over consistency, which may lead to inconsistencies in some cases.

		Does not impact our project, this is a problem for databases that have a lot of reading 
		and writing operations in parallel (transactional) .
-  **Query Complexity**: NoSQL databases may be less powerful for complex queries and aggregations compared to relational databases.
-  (**Lack of Standardization**: Because NoSQL databases encompass a wide range of technologies and approaches, selecting and using the right database for your specific requirements can be challenging.)

		Does not concern us.
-  (**Less Mature Tools and Technologies**: Compared to relational databases, there may be fewer mature tools, libraries, and frameworks available for NoSQL databases, although the ecosystem is constantly growing and evolving.)

		Does not concern us.
-  **Complex Queries**: Complex queries may require the use of special query syntaxes or aggregations, which can have a steep learning curve.

		This is a concern because SQL is a well kown query language (of course we have all passed 
		our SQL exam ;), learning  new ways to read and write the data can be time consuming.
### Conclusion
Since we are still in the development process and our data model could change in the future, we can benefit from a flexible model. Additionally, the data model structure could be simpler than that of a traditional SQL approach, where the data is divided across several tables. The price to pay for this is potentially a more difficult or less standardized way to query our data, but we believe that the benefits will outweigh the downsides.
## Comparison of MongoDB vs ElasticSearch
### MongoDB
#### Strengths
-   **Flexible Data Model**: MongoDB employs a flexible schema, allowing data to be stored without predefined structures. This facilitates easy scalability and modification of the data model.

		Major benefit for work in progress, change is possible even in later stages of the project.
-  **High Scalability**: MongoDB supports horizontal scaling through sharding, enabling large volumes of data to be distributed across multiple servers.

		No a big concern at the moment (see above).
-  **Rich Functionality**: It offers a wide range of features such as indexing, aggregation, replication, and geographic distribution.
		
		Nice to have.
-  **Community and Support**: MongoDB boasts a large and active developer community along with extensive documentation and support.

		Again, it is a potential benefit.

#### Weaknesses

-  **Consistency Model**: MongoDB defaults to a consistent model, which can sometimes result in performance degradation, especially during write operations.

		Consistency is no major concern for your project so this could be a neagative point. 
-  **Scalability Complexity**: While MongoDB supports horizontal scaling, configuring and managing sharding configurations requires a certain level of complexity.
	
		A weakness we will hopefully never be bothered with ;)

### Elasticsearch
#### Strengths
-  **Text Search and Full-Text Indexing**: Elasticsearch excels in full-text search and indexing of text data.

		No full-text search and indexing of text data once the data is tranformed and saved. We need some 
		help in the transformation part but in the moment the plan is to use  a geolocator for determining 
		the location and scrapy to build a list of skills, extract both the job title and experience level.
-  **Scalability**: Elasticsearch supports horizontal scaling through shard replication and the ability to distribute clusters across multiple nodes.

		No a big concern at the moment (see above).
-  **Real-Time Data Analysis**: Elasticsearch enables real-time data analysis and visualization, making it particularly useful for applications such as log analysis and monitoring.

		We don´t need real-time analysis.
-  **Ecosystem and Integration**: Elasticsearch is often used in conjunction with Logstash and Kibana to provide a complete ELK stack (Elasticsearch, Logstash, Kibana) for log analysis and visualization.

		Logstash may be a very handy tool for out project, however this part is currently done with 
		python scripts and will probably not change in the future due to time restrictions.
Weaknesses:

-  **Configuration Complexity**: Configuring and managing Elasticsearch clusters can be complex due to their distributed nature and the required indexing and replication.

			Same as MongoDB.
-  **Data Consistency**: Elasticsearch prioritizes performance and availability over consistency, which may lead to inconsistencies in some application scenarios.

		Again availability and consistency are no concerns of our project.
### Conclusion
Since we couldn't benefit from Elasticsearch's text search and potential transformation abilities, but we can potentially benefit from MongoDB's flexible data model and support resources, we have decided to choose MongoDB as our database for this project.