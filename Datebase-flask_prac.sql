-- 这个表用来记录访问主页的ip和时间
CREATE TABLE `visitRecord` (
  `recordId` int unsigned NOT NULL AUTO_INCREMENT,
  `ip` char(15) DEFAULT NULL,
  `visitTime` datetime DEFAULT NULL,
  PRIMARY KEY (`recordId`)
);

-- 这个表用来记录注册的用户相关信息
CREATE TABLE `user` (
  `userName` char(15) NOT NULL COMMENT '用户名',
  `userEmail` varchar(30) NOT NULL COMMENT '用户邮箱',
  `userpassWord` varchar(64) NOT NULL COMMENT '用户密码',
  `lastRegisterTime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `lastWithdrawTime` datetime DEFAULT NULL COMMENT '注销时间',
  `lastModifiedTime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最近修改时间',
  PRIMARY KEY (`userName`),
  UNIQUE KEY `userEmail` (`userEmail`)
);