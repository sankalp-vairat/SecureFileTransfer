

create database cn;

use cn;

create table ip_address (
name varchar(20),
address varchar(20),
port int(5),
primary key(address)
);


insert into ip_address values('PG14','<ip address>',5000);
insert into ip_address values('PG13','<ip address>',5001);
insert into ip_address values('PG15','<ip address>',5002);
insert into ip_address values('PG17','<ip address>',5003);
insert into ip_address values('PG18','<ip address>',5004);

select * from ip_address



create table hash_key (
address varchar(20) references ip_address(address),
hash_k varchar(500)
);

--------------------------------------------------------------------------------


create database ca;

use ca;
create table ip_address (
address varchar(20),
authorize varchar(1),
primary key(address)
);

insert into ip_address values('<ip address>','Y');
insert into ip_address values('<ip address>','Y');
insert into ip_address values('<ip address>','Y');
insert into ip_address values('<ip address>','Y');


select * from ip_address


SET SQL_SAFE_UPDATES=0;