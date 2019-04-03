CREATE TABLE `data` (  
    `id` int(11) NOT NULL AUTO_INCREMENT,  
    `date` datetime NOT NULL,  
    `vehicles` smallint NOT NULL,  
    `filename` varchar(512) NOT NULL,  
    PRIMARY KEY (`id`)) ENGINE=InnoDB