import itertools

class PRIterator:
    __doc__ = '''计算一张图中的PR值'''

    def __init__(self, graph):
        self.damping_factor = 0.85  # 阻尼系数,即α
        self.max_iterations = 100  # 最大迭代次数
        self.min_delta = 0.00001  # 确定迭代是否结束的参数,即ϵ
        self.graph = graph

    def page_rank(self):
        nodes = self.graph.nodes()
        flag = False

        if len(nodes) == 0:
            return {}

    #     如果节点没有出链，阻尼系数应为0。此处先给所有没有出链的节点加上到所有点的出链
        for node in nodes:
            if self.graph.out_degree(node) == 0:
                for node2 in nodes:
                    self.graph.add_edge(node, node2)

        # 初始化page_rank
        page_rank = dict.fromkeys(nodes, 1.0 / len(nodes))

        for n in range(self.max_iterations):
            change = 0
            for node in nodes:
                rank = 0
                for in_edge in self.graph.in_edges(
                        node):  #遍历所有对node有入链的点，取到相关的page_rank
                    rank += self.damping_factor * (page_rank[in_edge[0]] / self.
                                              graph.out_degree(in_edge[0]))
                rank += (1 - self.damping_factor) / len(nodes)

                change += abs(rank - page_rank[node])
                page_rank[node] = rank

            print("This is NO.{} iteration".format(n + 1))

            if change < self.min_delta:
                flag = True
                break
        if flag:
            print('finished in {}  iterations!'.format(node))
        else:
            print("finished out of 100 iterations!")
        return page_rank

class MapReduce:
    __doc__ = '''简单实现MapReduce功能'''

    @staticmethod
    def map_reduce(i, mapper, reducer):
        #     将key放在intermediate[i][0],value放在intermediate[i][1]
        intermediate = []
        for (key, value) in i.items():
            intermediate.extend(mapper(key, value))

        #     对key进行分组，key的值全部在groups[key]中以列表存储
        groups = {}
        for key, group in itertools.groupby(sorted(intermediate, key=lambda x: x[0]), key=lambda x: x[0]):
            groups[key] = [y for x, y in group]

        #     对值进行reducer计算
        return [reducer(intermediate_key, groups[intermediate_key]) for intermediate_key in groups]


class PRMapReduce:
    def __init__(self,
                 graph,
                 damping_factor=0.85,
                 max_iterations=100,
                 min_delta=0.00001):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.min_delta = min_delta
        self.num_of_pages = len(graph.nodes())
        # collections为key-value pair，其中key为网页，value[0]表示PageRank，value[1]表示出链数，value[2]表示出链的列表
        self.graph_collections = {}
        for node in graph.nodes():
            self.graph_collections[node] = [
                1.0 / self.num_of_pages,
                graph.out_degree(node),
                [edge[1] for edge in graph.out_edges(node)]
            ]

    def ip_mapper(self, input_key, input_value):
        '''
        对没有出链的网页进行处理，1：用来分组，没有特殊含义
        '''
        if input_value[1] == 0:
            return [(1, input_value[0])]
        else:
            return []

    def ip_reducer(self, input_key, input_value_list):
        '''
        对没有出链的网页PageRank值进行汇总，最终计算PageRank时直接划分到各个网页
        '''
        return sum(input_value_list)


    def pr_mapper(self, input_key, input_value):
        '''
        对有出链的网页，将该网页的PageRank值分到出链中
        '''
        return [(input_key, 0.0)] + [(out_link,
                                      input_value[0] / input_value[1])
                                     for out_link in input_value[2]]

    def pr_reducer(self, input_key, input_value_list, pr):
        '''
        更新所有input_key对应的PageRank值
        :param pr: 没有出链网页的PageRank之和
        :return: url和更新后的PageRank
        '''
        return (input_key, self.damping_factor * sum(input_value_list) +
                self.damping_factor * pr / self.num_of_pages +
                (1.0 - self.damping_factor) / self.num_of_pages)

    def page_rank(self):
        '''
        调用MapReduce，计算网页PageRank值
        :return:更新后的graph_collections
        '''
        flag = False
        #       对出链为空的网页进行处理，dangling_page为所有出链为空网页的PageRank之和
        dangling_list = MapReduce.map_reduce(self.graph_collections, self.ip_mapper,
                                   self.ip_reducer)
        if len(dangling_list) == 0:
            dangling_pr = 0
        else:
            dangling_pr = dangling_list[0]

        for i in range(self.max_iterations):
            change = 0

            new_pagerank = MapReduce.map_reduce(
                self.graph_collections, self.pr_mapper,
                lambda x, y: self.pr_reducer(x, y, dangling_pr))

            #             计算当前轮的改变值，然后更新PageRank
            for n in range(self.num_of_pages):
                change += abs(new_pagerank[n][1] - self.graph_collections[
                    new_pagerank[n][0]][0])
                self.graph_collections[new_pagerank[n][0]][0] = new_pagerank[n][1]

            print('Change: {}'.format(change))
            #             如果改变值小于最小限制，则跳出循环
            if change < self.min_delta:
                flag = True
                break

        if flag:
            print('finished in {} iterations'.format(i))
        else:
            print('finished out of {} iterations!'.format(self.max_iterations))

        return self.graph_collections