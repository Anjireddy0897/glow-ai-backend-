-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 28, 2026 at 06:51 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `antireddy`
--

-- --------------------------------------------------------

--
-- Table structure for table `ai_results`
--

CREATE TABLE `ai_results` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `skin_type` varchar(50) DEFAULT NULL,
  `issue` varchar(100) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `recommendation` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `skin_score` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ai_results`
--

INSERT INTO `ai_results` (`id`, `user_id`, `skin_type`, `issue`, `confidence`, `recommendation`, `created_at`, `skin_score`) VALUES
(5, 2, 'dry', 'acne', 66.3435, 'Use hydrating cleanser, Apply ceramide moisturizer, Avoid over-washing face', '2026-03-25 13:39:16', NULL),
(6, 2, 'oily', 'acne', 59.0147, 'Use Salicylic Acid face wash, Apply oil-free moisturizer, Use non-comedogenic sunscreen, Avoid fried and oily foods', '2026-03-25 13:39:40', NULL),
(7, 2, 'oily', 'acne', 59.0147, 'Use Salicylic Acid face wash, Apply oil-free moisturizer, Use non-comedogenic sunscreen, Avoid fried and oily foods', '2026-03-25 13:39:47', NULL),
(8, 2, 'normal', 'pimple', 97.5414, 'Use gentle cleanser, Apply light moisturizer, Use benzoyl peroxide spot treatment', '2026-03-25 13:40:09', NULL),
(9, 2, 'dry', 'pimple', 99.255, 'Use hydrating cleanser, Apply ceramide moisturizer, Use pimple patches', '2026-03-25 13:40:29', NULL),
(10, 2, 'dry', 'pimple', 99.255, 'Use hydrating cleanser, Apply ceramide moisturizer, Use pimple patches', '2026-03-25 13:40:34', NULL),
(11, 2, 'dry', 'dark_circle', 61.6806, 'Use thick hydrating eye cream, Apply hyaluronic acid serum under eyes, Drink more water', '2026-03-25 13:40:52', NULL),
(12, 2, 'normal', 'pigmentation', 48.1961, 'Use Vitamin C serum daily, Always apply SPF 50 sunscreen, Use gentle alpha arbutin serum', '2026-03-25 13:41:25', NULL),
(27, 10, 'normal', 'wrinkles', 80.7441, 'Vitamin C serum + Sunscreen', '2026-03-27 03:15:58', NULL),
(28, 10, 'dry', 'pigmentation', 89.5055, 'Hydrating moisturizer + Benzoyl peroxide', '2026-03-27 03:16:14', NULL),
(29, 10, 'dry', 'pigmentation', 89.5055, 'Hydrating moisturizer + Benzoyl peroxide', '2026-03-27 03:16:31', NULL),
(30, 10, 'dry', 'acne', 47.183, 'Hydrating moisturizer + Benzoyl peroxide', '2026-03-27 03:17:04', NULL),
(31, 10, 'normal', 'acne', 51.7136, 'Caffeine eye cream', '2026-03-27 03:17:18', NULL),
(33, 19, 'Normal', 'Acne', 81.16, 'Use gentle cleanser', '2026-03-27 05:30:11', 41),
(34, 10, 'Normal', 'Wrinkles', 61.51, 'Use anti-aging serum', '2026-03-27 06:51:09', 40),
(35, 10, 'oil', 'dark_circles', 50.7619, 'Oil-free moisturizer + Salicylic acid', '2026-03-27 07:03:15', NULL),
(36, 10, 'normal', 'dark_circles', 76.5509, 'Caffeine eye cream', '2026-03-27 07:03:33', NULL),
(37, 10, 'normal', 'wrinkles', 80.7441, 'Vitamin C serum + Sunscreen', '2026-03-27 07:04:19', NULL),
(38, 10, 'normal', 'acne', 59.2961, 'Caffeine eye cream', '2026-03-27 07:16:20', NULL),
(39, 10, 'Normal', 'Wrinkles', 61.51, 'Use anti-aging serum', '2026-03-27 07:18:45', 40),
(40, 10, 'Normal', 'Wrinkles', 61.51, 'Use anti-aging serum', '2026-03-27 07:32:27', 40),
(41, 10, 'oil', 'redness', 53.9939, 'Consult dermatologist', '2026-03-27 07:38:46', NULL),
(42, 10, 'normal', 'wrinkles', 80.7441, 'Vitamin C serum + Sunscreen', '2026-03-27 07:40:50', NULL),
(43, 10, 'Normal', 'Wrinkles', 61.51, 'Use anti-aging serum', '2026-03-27 07:53:38', 40),
(45, 20, 'Normal', 'Wrinkles', 61.51, 'Use anti-aging serum', '2026-03-27 08:05:51', 40),
(51, 21, 'normal', 'wrinkles', 76.2355, 'Vitamin C serum + Sunscreen', '2026-03-27 08:22:23', 57),
(52, 21, 'Oil', 'Dark_circles', 97.54, 'Consult dermatologist', '2026-03-27 08:23:06', 49),
(57, 22, 'dry', 'acne', 61.4819, 'Hydrating moisturizer + Benzoyl peroxide', '2026-03-27 09:44:37', 47),
(58, 23, 'normal', 'dark_circles', 70.4185, 'Caffeine eye cream', '2026-03-28 03:42:17', 40),
(59, 24, 'normal', 'dark_circles', 70.4185, 'Caffeine eye cream', '2026-03-28 04:10:17', 40),
(60, 25, 'normal', 'wrinkles', 57.0218, 'Vitamin C serum + Sunscreen', '2026-03-28 04:36:14', 44),
(61, 10, 'normal', 'wrinkles', 73.244, 'Vitamin C serum + Sunscreen', '2026-03-28 04:44:51', 49),
(62, 2, 'dry', 'wrinkles', 80.359, 'Retinol cream + Heavy moisturizer', '2026-03-28 04:50:05', 40),
(63, 22, 'dry', 'wrinkles', 80.359, 'Retinol cream + Heavy moisturizer', '2026-03-28 04:52:24', 40),
(64, 22, 'dry', 'wrinkles', 39.459, 'Retinol cream + Heavy moisturizer', '2026-03-28 04:52:36', 48),
(65, 22, 'dry', 'pigmentation', 78.6842, 'Hydrating moisturizer + Benzoyl peroxide', '2026-03-28 04:52:57', 64),
(66, 22, 'normal', 'acne', 51.4635, 'Consult dermatologist', '2026-03-28 05:09:33', 40),
(67, 26, 'normal', 'wrinkles', 76.2355, 'Consult dermatologist', '2026-03-28 05:14:27', 57),
(68, 26, 'normal', 'wrinkles', 76.2355, 'Consult dermatologist', '2026-03-28 05:23:06', 57),
(69, 22, 'normal', 'acne', 51.4635, 'Consult dermatologist', '2026-03-28 05:24:51', 40),
(70, 22, 'normal', 'acne', 51.4635, 'Consult dermatologist', '2026-03-28 05:28:23', 40),
(71, 22, 'normal', 'acne', 51.4635, 'Consult dermatologist', '2026-03-28 05:28:42', 40),
(72, 22, 'normal', 'acne', 51.4635, 'Consult dermatologist', '2026-03-28 05:28:46', 40),
(73, 22, 'dry', 'pores', 94.5919, 'Consult dermatologist', '2026-03-28 05:29:01', 58),
(74, 26, 'dry', 'pores', 94.5919, 'Consult dermatologist', '2026-03-28 05:34:30', 58),
(75, 5, 'dry', 'pores', 94.5919, 'Consult dermatologist', '2026-03-28 05:35:30', 58),
(76, 27, 'oil', 'wrinkles', 47.1553, 'Consult dermatologist', '2026-03-28 05:41:46', 49);

-- --------------------------------------------------------

--
-- Table structure for table `recommendation`
--

CREATE TABLE `recommendation` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `product` varchar(255) DEFAULT NULL,
  `skin_score` decimal(10,2) DEFAULT NULL,
  `skin_type` varchar(100) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `recommendation`
--

INSERT INTO `recommendation` (`id`, `user_id`, `product`, `skin_score`, `skin_type`, `status`, `created_at`) VALUES
(22, 10, 'AI Analysis', 40.00, 'Normal', 'completed', '2026-03-27 04:12:12'),
(23, 10, 'AI Analysis', 40.00, 'Dry', 'completed', '2026-03-27 04:13:14'),
(24, 10, 'AI Analysis', 40.00, 'Dry', 'completed', '2026-03-27 04:13:31'),
(25, 10, 'AI Analysis', 45.00, 'Normal', 'completed', '2026-03-27 04:16:35'),
(26, 10, 'AI Analysis', 45.00, 'Normal', 'completed', '2026-03-27 04:27:18'),
(27, 10, 'AI Analysis', 48.00, 'Oil', 'completed', '2026-03-27 04:28:41'),
(28, 10, 'AI Analysis', 40.00, 'Oil', 'completed', '2026-03-27 04:29:12'),
(29, 10, 'AI Analysis', 40.00, 'Oil', 'completed', '2026-03-27 04:29:54'),
(30, 10, 'AI Analysis', 40.00, 'Oil', 'completed', '2026-03-27 04:33:09'),
(31, 10, 'AI Analysis', 40.00, 'Oil', 'completed', '2026-03-27 04:35:09'),
(32, 10, 'AI Analysis', 48.00, 'Oil', 'completed', '2026-03-27 04:35:26'),
(33, 10, 'AI Analysis', 50.00, 'Normal', 'completed', '2026-03-27 04:40:39'),
(34, 10, 'AI Analysis', 40.00, 'Dry', 'completed', '2026-03-27 04:42:24'),
(35, 10, 'AI Analysis', 40.00, 'Dry', 'completed', '2026-03-27 04:46:10'),
(36, 10, 'AI Analysis', 46.00, 'Dry', 'completed', '2026-03-27 04:46:45'),
(37, 10, 'AI Analysis', 46.00, 'Dry', 'completed', '2026-03-27 04:52:37'),
(38, 10, 'AI Analysis', 74.00, 'Dry', 'completed', '2026-03-27 05:00:50'),
(39, 10, 'AI Analysis', 53.00, 'Dry', 'completed', '2026-03-27 05:02:53'),
(40, 10, 'AI Analysis', 74.00, 'Dry', 'completed', '2026-03-27 05:05:30'),
(41, 10, 'AI Analysis', 74.00, 'Dry', 'completed', '2026-03-27 05:12:20'),
(42, 10, 'AI Analysis', 74.00, 'Dry', 'completed', '2026-03-27 05:23:47'),
(43, 10, 'Oil-free moisturizer + Salicylic acid', 64.00, 'oil', 'completed', '2026-03-27 07:03:15'),
(44, 10, 'Caffeine eye cream', 67.00, 'normal', 'completed', '2026-03-27 07:03:33'),
(45, 10, 'Vitamin C serum + Sunscreen', 70.00, 'normal', 'completed', '2026-03-27 07:04:19'),
(46, 10, 'Caffeine eye cream', 71.00, 'normal', 'completed', '2026-03-27 07:16:20'),
(47, 10, 'Consult dermatologist', 81.00, 'oil', 'completed', '2026-03-27 07:38:46'),
(48, 10, 'Vitamin C serum + Sunscreen', 70.00, 'normal', 'completed', '2026-03-27 07:40:50'),
(49, 20, 'Vitamin C serum + Sunscreen', 70.00, 'normal', 'completed', '2026-03-27 08:03:26'),
(50, 21, 'Vitamin C serum + Sunscreen', 71.00, 'normal', 'completed', '2026-03-27 08:18:59'),
(51, 21, 'Retinol cream + Heavy moisturizer', 70.00, 'dry', 'completed', '2026-03-27 08:19:32'),
(52, 21, 'Consult dermatologist', 76.00, 'normal', 'completed', '2026-03-27 08:20:12'),
(53, 21, 'Vitamin C serum + Sunscreen', 70.00, 'normal', 'completed', '2026-03-27 08:20:38'),
(54, 21, 'Oil-free moisturizer + Salicylic acid', 61.00, 'oil', 'completed', '2026-03-27 08:21:07'),
(55, 21, 'Vitamin C serum + Sunscreen', 57.00, 'normal', 'completed', '2026-03-27 08:22:23'),
(56, 10, 'Caffeine eye cream', 75.00, 'normal', 'completed', '2026-03-27 09:09:05'),
(57, 22, 'Hydrating moisturizer + Benzoyl peroxide', 62.00, 'dry', 'completed', '2026-03-27 09:29:21'),
(58, 22, 'Caffeine eye cream', 70.00, 'normal', 'completed', '2026-03-27 09:30:09'),
(59, 22, 'Vitamin C serum + Sunscreen', 61.00, 'normal', 'completed', '2026-03-27 09:35:08'),
(60, 22, 'Hydrating moisturizer + Benzoyl peroxide', 47.00, 'dry', 'completed', '2026-03-27 09:44:37'),
(61, 23, 'Caffeine eye cream', 40.00, 'normal', 'completed', '2026-03-28 03:42:17');

-- --------------------------------------------------------

--
-- Table structure for table `skin_surveys`
--

CREATE TABLE `skin_surveys` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `skin_type` varchar(100) DEFAULT NULL,
  `concerns` text DEFAULT NULL,
  `sensitivity` varchar(100) DEFAULT NULL,
  `climate` varchar(100) DEFAULT NULL,
  `ingredients` text DEFAULT NULL,
  `allergies` text DEFAULT NULL,
  `skin_score` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `age` varchar(10) DEFAULT NULL,
  `gender` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `full_name`, `age`, `gender`) VALUES
(1, 'dhatch5u@sgmail.com', '$2b$12$3M8e3AG5thZ/a8BJExVjLOY.ln.Esppw9ruQG2j3enjHgDLxm1pLC', 'Test User', '22', 'Male'),
(2, 'dhatch5u@gmail.com', '$2b$12$JwJ0NwoFuLa7C5YkeUxFJOaGppvsQ.6X9wKdnmGUCsMiL6urM7f4.', 'Test User', '22', 'Male'),
(3, 'chandu@gmail.com', '$2b$12$DX.dIDnuYLj.oC.U.rwJYuqXLbejEdwBSVONAy0yTd1BFq3Z9s92e', 'Chandu1', '22', 'Male'),
(4, 'anjireddy@gmail.com', '$2b$12$51GOxIc2aWPeUY16tx9z.uRg3ijSp/3kqY50N9nVk0dZEXjLFPesK', 'anjireddy', '22', 'male'),
(5, 'anjireddy1@gmail.com', '$2b$12$EeuraVKac0RGR1r1OgQHnuJHZmkHZ6WQKwFYYbt8OPqTL3NQgNyRq', 'ANJIREDDY', '22', 'Male'),
(6, 'vineeth@gmail.com', '$2b$12$kjgW/oPzcHkPJ46hvaJPsut5Vq8nyrS3u6ZU28RBVveJ7cV4/KISK', 'Vineeth', '23', 'Male'),
(7, 'raja@gmail.com', '$2b$12$FCoTIcE13hFfBq1r1q3uzebeeg/3FFHUmOIyJ6UUOIAbqWYEylPgS', 'Rajareddy', '23', 'Male'),
(8, 'pin@gmail.com', '$2b$12$V7aUFCZYXillvT9UyyPxheD9E1InCCDnfjOT8.1XHGkN2w9dLh/hS', 'Pin', '22', 'Male'),
(9, 'chandureddyb6214@gmail.com', '$2b$12$Q4/U0xuysfLn0r.n7ghBjeaML9OUuLqvaVFQrLFdT0ZJooFe/hSHu', 'can', '44', 'Male'),
(10, 'kanjireddy2020@gmail.com', '$2b$12$L1wgcpCz1NjivOwtM.HpLOyIHkL4tQlf4UaReUgUa4DTfNA71fUHO', 'Kesara Anjireddy', '23', 'Male'),
(11, 'brosai@gmail.com', '$2b$12$NrKjFAu.bNvCIAQGiEd2ZeOXcJpK2tXMFdNx4e6m1CRoMob5Br6By', 'brosai', '23', 'Male'),
(12, 'wow@gmail.i', '$2b$12$zhXFzhiSPzObGycvXmqHje7iudJmB0nngHqTBP9PGC9rn93kYEbQ.', 'wiw', '44', 'Male'),
(13, 'malli@gmail.com', '$2b$12$XnrZ6ZcA49YBSrz8hTCZjuLxSKjC2E04R7sR3lWztPR2in1KDK6ta', 'malli', '23', 'Male'),
(14, 'redd@gmail.com', '$2b$12$Y8Wt/wmLJHhAfJS4BAwr5OjAedZXDiqJik8bp0JJgr3xiJvfO0pL6', 'reddy', '23', 'Male'),
(15, 'anjireddy2004@gmail.com', '$2b$12$rqaBM6vxtWDHVj1zeyQgZuL5bu79hSMUbsd16x1MxJ./NdSoB2n8m', 'anjireddy1', '22', 'Male'),
(16, 'anjireddy12@gmail.com', '$2b$12$9qbe8RU2rVZg6XoACY3rmOePhcgPun4K3LQbmvan/v410zyB1ySWK', 'ANJIREDDY', '22', 'Male'),
(17, 'kiran@gmaul.com', '$2b$12$Ygx2hNEKWKXOXbN7uUJw3e8g2MCCPpC6WpW49lbXi6xebJxs/h8e6', 'kiran', '23', 'Male'),
(18, 'vishnu@gmail.com', '$2b$12$BqKV6/7QbBz5vxLAVsH50ubfl6AZNgseRBfMblPQt53ZjDqAcquDu', 'vishnu', '22', 'Male'),
(19, 'srinivasvellaturi61@gmail.com', '$2b$12$pcQcoClSTnDii5.qIHKNq.l3h3.Hdky74xZ7E1pSC3Niep6ZXCT4a', 'srinivas', '22', 'Male'),
(20, 'jack@gmail.com', '$2b$12$1mcFc1MURtLrMFAyzojCF.pln13JYP3VKZY0xZScSQIPtxzwIvboe', 'jack', '24', 'Male'),
(21, 'yaswathc250@gmail.com', '$2b$12$YYTRJeQDbQt/wXpQsA1oEuK3D1nF7IYULhNmwjjV0WCOaCEe757fS', 'yaswanth', '21', 'Male'),
(22, 'pavan@gmail.com', '$2b$12$Vji9elscR5L4CDuBDXMs0u98drEwH5KatRvKufEXViXixYbNHGjM2', 'pavan', '23', 'Male'),
(23, 'pandu@gmail.com', '$2b$12$K//Ce6aKVkX8lK7Xn9fcF.fHlFKcfXUnCRYPqj6KstHuxsxueOg.K', 'pandyu', '23', 'Male'),
(24, 'bhagya@gmqil.com', '$2b$12$YFtQiGTqbooukMflWB1g2exPmXyjTJ4d8urJs6i4fqoMH0xlunXHG', 'Bhagya lakshmi', '38', 'Male'),
(25, 'parlapallisomasekhar@gmail.com', '$2b$12$QkgLGXAXrueQfUBQ6HX2FORQsVZk5jbRQJiNGYxiyvYFke8ekMRuu', 'somasekhar', '42', 'Male'),
(26, 'nani@gmail.com', '$2b$12$CpudRqACMM4JMP94Dveb5uQOYp.8Ct96mNTJGQvnSvzPRw5bnmZ76', 'nani', '23', 'Male'),
(27, 'sanjaykuruvella112@gmail.com', '$2b$12$h0EWEM4KT2RPR2KT5c.5Du5RH/P5kE1lpgcaPwWwWSqQ4fNCN0Avy', 'anji', '21', 'Male');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ai_results`
--
ALTER TABLE `ai_results`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `recommendation`
--
ALTER TABLE `recommendation`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `skin_surveys`
--
ALTER TABLE `skin_surveys`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ai_results`
--
ALTER TABLE `ai_results`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `recommendation`
--
ALTER TABLE `recommendation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT for table `skin_surveys`
--
ALTER TABLE `skin_surveys`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ai_results`
--
ALTER TABLE `ai_results`
  ADD CONSTRAINT `ai_results_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
