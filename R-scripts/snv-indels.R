library(ggplot2)

onco = read.xlsx("Oncomine_EXaCT-1_VAF-DP.xlsx")
#onco_subset = subset(onco, exact1.tcov >= 30 & oncomine.tcov >= 400 & exact1.vaf >= 0.10 & oncomine.vaf >= 0.05)
#onco_subset = subset(onco, exact1.tcov >= 30 & oncomine.tcov >= 400)
onco_subset2 = subset(onco, exact1.tcov != 0)

onco_plot = ggplot(onco, aes(x = oncomine.vaf, y = exact1.vaf, color = exact1.tcov > 0)) + 
  geom_point(aes(size = exact1.tcov)) +
  ylab("EXaCT-1 VAF") + xlab("Oncomine VAF") + geom_hline(yintercept = 0.1) + geom_vline(xintercept = 0.05) +
  scale_color_manual(name = "Coverage", values = setNames(c('black','red'),c(T, F)))

onco_plot

onco_subset_plot = ggplot(onco_subset2, aes(x = oncomine.vaf, y = exact1.vaf)) + 
  geom_point(aes(size = log10(exact1.tcov))) + ylab("EXaCT-1 VAF") + xlab("Oncomine VAF") +
  geom_hline(yintercept = 0.1) + geom_vline(xintercept = 0.05) +
  geom_abline(slope = 1, intercept = 0) +
  scale_x_continuous(limits = c(0, 1)) +
  scale_y_continuous(limits = c(0, 1))

onco_subset_plot


cor.test(onco_subset$oncomine.vaf, onco_subset$exact1.tcov, method = "pearson")
cor.test(onco_subset$oncomine.tcov, onco_subset$exact1.tcov, method = "pearson")
#cor.test(onco_subset$oncomine.vaf, onco_subset$oncomine.tcov, method = "pearson", conf.level = 0.95)
