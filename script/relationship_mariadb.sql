SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE `relationship` (
  `id` int(11) NOT NULL,
  `user_name` varchar(256) NOT NULL DEFAULT '0',
  `level` varchar(256) NOT NULL DEFAULT '0',
  `referer` varchar(256) NOT NULL DEFAULT '0',
  `type` varchar(256) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='github_relationship的MariaDB实现';


ALTER TABLE `relationship`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_name` (`user_name`),
  ADD KEY `level` (`level`),
  ADD KEY `referer` (`referer`),
  ADD KEY `type` (`type`);

ALTER TABLE `relationship`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
