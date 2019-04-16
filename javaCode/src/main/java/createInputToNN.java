
import org.jgrapht.DirectedGraph;
import org.jgrapht.GraphPath;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultDirectedGraph;
import org.jgrapht.graph.DefaultEdge;
import java.io.*;
import java.util.*;


public class createInputToNN {
 public static int calculateNumOfPaths_count = 1;

    public static void main(String[] args) throws ClassNotFoundException, IOException {
        System.out.println("\n--------Start Create Input To NN----------\n");
        String FULL_ADDITIONAL_FILES_PATH= null;
        String CALL_GRAPH_PATH= null;
        String TRACE_FILE_PATH= null;
        String LOG_FILE= null;
        String[] bugFuncNames = new String[10];
        String bugNum = "-1";

        if(args.length>1)
        {
            System.out.println("\n--------Got Two Arguments----------");
            FULL_ADDITIONAL_FILES_PATH = args[0];
            CALL_GRAPH_PATH = FULL_ADDITIONAL_FILES_PATH + "\\callGraph.txt";
			TRACE_FILE_PATH = FULL_ADDITIONAL_FILES_PATH + "\\traceFile.txt";
            String input_bug_functions = args[1];
            bugFuncNames = input_bug_functions.split(" ");
            LOG_FILE = args[2];
            bugNum = args[3];
        }
        else {
            System.exit(1);
        }
        int lineLength = 11;

        Map<String, List<String>> traceDic = new HashMap<String, List<String>>();
        List<String> testsList = new ArrayList<>();
        Map<String, Integer> funcRank = new HashMap<String, Integer>();

        readTraceFile(TRACE_FILE_PATH, traceDic,testsList,funcRank);
        List<String> targetFunctionList = new ArrayList<>(funcRank.keySet());

        //////create call graph//////////////
        System.out.println("--------CREATE CALL GRAPH----------");
        ////////////////todo get call graph first/////////////////////////
        Map<String, LinkedHashSet<String>> callGraph;
        Map<String, Integer> vertexDic  = new HashMap<String, Integer>();
        Map<String, Integer> functionVertexDic  = new HashMap<String, Integer>();
        Map<String, Integer> testVertexDic  = new HashMap<String, Integer>();
        callGraph = createCallGraph(CALL_GRAPH_PATH,vertexDic,functionVertexDic,testVertexDic);
        int [][] adjMatrix = new int[vertexDic.size()][vertexDic.size()];
        DirectedGraph<String, DefaultEdge> directedGraph = createGraph(callGraph,adjMatrix, vertexDic);

        System.out.println("--------CALCULATE PATHS----------");
//        int [][] pathCount = calculateNumOfPaths(adjMatrix);
        int [][] pathCount = new int[5][];

        ////////////////todo get DebuggerTests/////////////////////////

        File traceFolder = new File(FULL_ADDITIONAL_FILES_PATH + "\\DebuggerTests");

        FileWriter trainingWriter = new FileWriter(FULL_ADDITIONAL_FILES_PATH + "\\trainingInputToNN.csv");
        FileWriter predictWriter = new FileWriter(FULL_ADDITIONAL_FILES_PATH + "\\predictionInputToNN.csv");
        System.out.println("--------WRITING THE INPUT FILE----------");
        insertIndexToCSV(lineLength ,trainingWriter);
        insertIndexToCSV(lineLength ,predictWriter);
        boolean belongToTrain;
        for (int i = 0; i < targetFunctionList.size(); i++) {
            if (i % 1000 == 0) {
                int percent = (int) ((i * 100.0f) / targetFunctionList.size());
                System.out.println(percent + "% of the functions were finished");
            }
            String targetFunction = targetFunctionList.get(i);
            belongToTrain = false;
            if (i % 20 == 0) {
                belongToTrain = true;
            }

            createCSV(testsList, traceFolder, targetFunction, directedGraph, trainingWriter,predictWriter, lineLength, pathCount, vertexDic,traceDic,belongToTrain);
        }
        returnError(FULL_ADDITIONAL_FILES_PATH + "\\errorFile.txt", 0);

        trainingWriter.close();
        predictWriter.close();
        System.out.println("--------The End Of Create Input To NN----------\n\n");
    }

    private static int numOfOccurrences(Map<String,List<String>> traceDic, String functionName) {
        int count = 0;
        Set<String> setOfKeys = traceDic.keySet();
        for(String testName : setOfKeys){
            if(traceDic.get(testName).contains(functionName))
            {
                count++;
            }
        }
        return count;
    }

    private static void readTraceFile(String traceFilePath, Map<String,List<String>> traceDic, List<String> testsList, Map<String,Integer> funcRank) throws IOException {

        try (BufferedReader br = new BufferedReader(new FileReader(traceFilePath))) {
            String line,testName,traceList,funcNameToInsert;
            String[] testTrace;
            int lastIndex=0;
            testName= "";
            while ((line = br.readLine()) != null) {
                if (line.contains("#test#")){
                    line = line.replace("#test#", "");
                    testName = line;
                    lastIndex = line.lastIndexOf(".");
                    if(lastIndex>0)
                    {
                        testName = line.substring(0,lastIndex) + ':' + line.substring(lastIndex+1);
                    }

                    testsList.add(testName);
                    traceDic.put(testName, new ArrayList<String>());
                }
                else{
                    traceList = line.replace("#trace#", "");
                    testTrace = traceList.split("@");
                    for(String func : testTrace)
                    {
                        if(!func.equals(""))
                        {
                            if(func.indexOf("(") != -1)
                            {
                                func = func.substring(0,func.indexOf("("));
                            }
                            funcNameToInsert = func;
                            lastIndex = func.lastIndexOf(".");
                            if(lastIndex>0)
                            {
                                funcNameToInsert = func.substring(0,lastIndex) + ':' + func.substring(lastIndex+1);
                            }
                            funcNameToInsert = changeConstructorName(funcNameToInsert);
                            traceDic.get(testName).add(funcNameToInsert);
                            if (funcRank.containsKey(funcNameToInsert)) {
                                funcRank.put(funcNameToInsert, funcRank.get(funcNameToInsert) + 1);
                            } else {
                                funcRank.put(funcNameToInsert, 1);
                            }
                        }
                    }
                }
            }
        }
    }

    private static String changeConstructorName(String funcNameToInsert) {
        String [] splited = funcNameToInsert.split(":");
        String result = funcNameToInsert;
        int lastIndex = splited[0].lastIndexOf(".");
        if(lastIndex>0 && splited[0].substring(lastIndex + 1,splited[0].length()).equals(splited[1]))
        {
            splited[1] = "<init>";
            result = String.join(":",splited);
        }

        return result;

    }

    private static void writeToLog(String log_file, String s, String bugNum) throws IOException {
        FileWriter fw = new FileWriter(log_file,true); //the true will append the new data
        fw.write("Bug Num:" +bugNum+ ", " + s + "\r\n");//appends the string to the file
        fw.close();
    }

    private static void returnError(String errorFilePath, int i) throws FileNotFoundException, UnsupportedEncodingException {
        PrintWriter writer = new PrintWriter(errorFilePath, "UTF-8");
        writer.println(Integer.toString(i));
        writer.close();
    }

    private static int[][] calculateNumOfPaths(int[][] adjMatrix) {
        int[][] a = new int[adjMatrix.length][adjMatrix.length];
        int[][] b = new int[adjMatrix.length][adjMatrix.length];
        int[][] c = new int[adjMatrix.length][adjMatrix.length];
        int[][] count = new int[adjMatrix.length][adjMatrix.length];
        for(int i=0; i<adjMatrix.length; i++)
            for(int j=0; j<adjMatrix[i].length; j++)
            {
                a[i][j] = adjMatrix[i][j];
                b[i][j] = adjMatrix[i][j];
                count[i][j] = adjMatrix[i][j];
            }
        for(int iter =0; iter < calculateNumOfPaths_count; iter ++)
        {
            System.out.println("calculate paths with length:" + (iter+1));

            for (int i=0; i<adjMatrix.length; ++i)
                for (int j=0; j<adjMatrix.length; ++j)
                {
                    for (int k=0; k<adjMatrix.length; ++k)
                    {
                        c[i][j] += a[i][k] * b[k][j];
                    }
                    count[i][j] += c[i][j];
                }
            for(int i=0; i<c.length; i++)
                for(int j=0; j<c[i].length; j++)
                {
                    a[i][j] = c[i][j];
                    c[i][j] = 0;
                }
        }
        return count;
    }



    private static DirectedGraph<String, DefaultEdge> createGraph(Map<String, LinkedHashSet<String>> callGraph, int[][] adjMatrix, Map<String, Integer> vertexDic) {

        DirectedGraph<String, DefaultEdge> directedGraph = new DefaultDirectedGraph<>(DefaultEdge.class);
        Set<String> s = callGraph.keySet();
        int vertex1,vertex2;
        for (String v:s) {
            if(!directedGraph.containsVertex(v))
                directedGraph.addVertex(v);
            LinkedHashSet<String> edges = callGraph.get(v);
            for (String v2:edges) {
                if(!directedGraph.containsVertex(v2))
                    directedGraph.addVertex(v2);

                if(!directedGraph.containsEdge(v,v2))
                {
                    directedGraph.addEdge(v,v2);
                    vertex1 = vertexDic.get(v);
                    vertex2 = vertexDic.get(v2);
                    if(vertex1 >= 0 && vertex2 >= 0)
                        adjMatrix[vertex1][vertex2] = 1;
                }
            }
        }
        return directedGraph;
    }

    private static void insertIndexToCSV(int lineLength, FileWriter writer) throws IOException {
        String[] columnsArray = {"FuncName", "TestName", "y", "PathLength", "FuncInDegree", "TestOutDegree",
        "PathExistence", "ClassCommonWords", "FuncCommonWords", "ClassSim", "FuncSim"};
        for (int j = 0; j < columnsArray.length; j++) {
            writer.append(columnsArray[j]);
            if(j<columnsArray.length-1)
                writer.append(",");
        }
        writer.append("\n");
    }



    private static int createCSV(List<String> testClassList, File testFolder, String targetFunction, DirectedGraph<String, DefaultEdge> callGraph, FileWriter trainingWriter, FileWriter predictWriter, int lineLength, int[][] pathCount, Map<String, Integer> vertexDic, Map<String, List<String>> traceDic,boolean belongToTraining) throws IOException {

        String lineArray[] = new String[lineLength];
        int wroteLine = 0;
        File[] files = testFolder.listFiles();
        int pathLength,numberOfPath;
        for (String sourceFunction:testClassList)
        {
            lineArray[0] = targetFunction; //enter function name
            lineArray[1] = sourceFunction; //enter test name
            assert files != null;
            lineArray[2] = String.valueOf(isItContainTarget(sourceFunction,targetFunction,traceDic)); // 1/0 if the function is in the trace
            pathLength = getPathLength(callGraph,sourceFunction,targetFunction);
            lineArray[3] = String.valueOf(pathLength); // enter path length


            if(callGraph.containsVertex(targetFunction))
                lineArray[4] = String.valueOf(callGraph.inDegreeOf(targetFunction)); //enter the function degree in the graph
            else
                lineArray[4] = String.valueOf(0);

            if(callGraph.containsVertex(sourceFunction))
                lineArray[5] = String.valueOf(callGraph.outDegreeOf(sourceFunction)); //enter the test out degree in the graph
            else
                lineArray[5] = String.valueOf(0);
            numberOfPath = 0;
            if(lineArray[3].equals("9999"))
            {
                numberOfPath = 0;
            }
            else if(vertexDic.get(sourceFunction) != null && vertexDic.get(targetFunction) != null)
            {
                numberOfPath = 1;
//                numberOfPath = getNumOfPath(callGraph,sourceFunction,targetFunction,2);
//                numberOfPath = pathCount[vertexDic.get(sourceFunction)][vertexDic.get(targetFunction)];
            }

            lineArray[6] = String.valueOf(numberOfPath); // enter the number of difference paths
            lineArray[7] = nameSimilarity(targetFunction.substring(targetFunction.lastIndexOf(".") + 1,targetFunction.indexOf(":")),sourceFunction.substring(sourceFunction.lastIndexOf(".") + 1,sourceFunction.indexOf(":"))); //class name similarity
            lineArray[8] = nameSimilarity(targetFunction.split(":")[1],sourceFunction.split(":")[1]); //function name similarity

            String simTest = sourceFunction.replace("Test","").replace("test","");

            lineArray[9] = similarity(classNameFromPath(targetFunction),classNameFromPath(simTest));
            lineArray[10] = similarity(funcNameFromPath(targetFunction),funcNameFromPath(simTest));

            writeLineToCSV(lineArray,predictWriter);
            if(belongToTraining)
                writeLineToCSV(lineArray,trainingWriter);
            wroteLine = 1;
        }
        return wroteLine;
    }

    private static String funcNameFromPath(String t) {
        String[] splited = t.split(":");
        if (splited.length>1)
        {
            return splited[1];
        }
        return "asdlkfdgklerkmsvlksdflkejwrkljdf;kl";
    }

    private static String classNameFromPath(String t) {
        String res = t.substring(t.lastIndexOf(".") + 1,t.indexOf(":"));
        return res;
    }

    public static String similarity(String s1, String s2) {
        String longer = s1, shorter = s2;
        if (s1.length() < s2.length()) { // longer should always have greater length
            longer = s2; shorter = s1;
        }
        int longerLength = longer.length();
        if (longerLength == 0) { return "1"; /* both strings are zero length */ }
        return String.valueOf((longerLength - editDistance(longer, shorter)) / (double) longerLength);
    }

    public static int editDistance(String s1, String s2) {
        s1 = s1.toLowerCase();
        s2 = s2.toLowerCase();

        int[] costs = new int[s2.length() + 1];
        for (int i = 0; i <= s1.length(); i++) {
            int lastValue = i;
            for (int j = 0; j <= s2.length(); j++) {
                if (i == 0)
                    costs[j] = j;
                else {
                    if (j > 0) {
                        int newValue = costs[j - 1];
                        if (s1.charAt(i - 1) != s2.charAt(j - 1))
                            newValue = Math.min(Math.min(newValue, lastValue),
                                    costs[j]) + 1;
                        costs[j - 1] = lastValue;
                        lastValue = newValue;
                    }
                }
            }
            if (i > 0)
                costs[s2.length()] = lastValue;
        }
        return costs[s2.length()];
    }

    private static String nameSimilarity(String function, String test) {

        int count = 0;
        String[] splitedFunction = function.split("(?=\\p{Upper})");
        String[] splitedTest = test.split("(?=\\p{Upper})");
        for(String word : splitedFunction)
        {
            if(Arrays.asList(splitedTest).contains(word))
            {
                count ++;
            }
        }

        return String.valueOf(count);
    }

    private static int isItContainTarget(String test, String function, Map<String, List<String>> traceDic) {
        if(!traceDic.containsKey(test))
            return 0;
        if(traceDic.get(test).contains(function))
        {
            return 1;
        }
        return 0;

    }

    private static int getPathLength(DirectedGraph<String, DefaultEdge> callGraph, String s, String t) {
        GraphPath<String, DefaultEdge> path;
        DijkstraShortestPath<String, DefaultEdge> dijkstraShortestPath
                = new DijkstraShortestPath<>(callGraph);
        if(callGraph.containsVertex(s) && callGraph.containsVertex(t))
            path = dijkstraShortestPath.getPath(s,t);
        else
            return 9999;
        if(path!=null)
            return path.getLength();

        return 9999;
    }

    private static Map<String,LinkedHashSet<String>> createCallGraph(String path, Map<String, Integer> vertexDic, Map<String, Integer> functionVertexDic, Map<String, Integer> testVertexDic) throws IOException {
        Map<String, LinkedHashSet<String>> callGraph = new HashMap<String, LinkedHashSet<String>>();
        LinkedHashSet<String> value;
        String targetType;
        int[] vertexArrayIndex = new int[3];
        int vertexIndex = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line;
            int indexToSplit;
            String[] splited;
            while ((line = br.readLine()) != null) {
                if(line.startsWith("M:")){
                    splited = line.split(" ");
                    splited[0] = cleanString(splited[0]);
                    //add ":" to splited[1] for cleaning the string
                    splited[1] = splited[1].substring(0, 3) + ":" + splited[1].substring(3, splited[1].length());
                    targetType = splited[1].substring(0, 3);
                    splited[1] = cleanString(splited[1]);

                    if(!splited[1].contains("$") && !targetType.equals("(I)"))
                        vertexIndex = enterEdge(callGraph, splited,vertexDic,vertexIndex);
                    else
                        indexToSplit = 3;
                }
            }
        }
        return callGraph;
    }

    private static int enterEdge(Map<String, LinkedHashSet<String>> callGraph, String[] splited, Map<String, Integer> vertexDic, int vertexIndex) {
        LinkedHashSet<String> value;
        splited[0] = removeDollar(splited[0]);
        splited[1] = removeDollar(splited[1]);
        if(!splited[0].equals(splited[1]) && (splited[1].contains("org")) && (splited[0].contains("org")))
        {

            if(!vertexDic.containsKey(splited[0]))
            {
                vertexDic.put(splited[0],vertexIndex);
                vertexIndex++;
            }
            if(!vertexDic.containsKey(splited[1]))
            {
                vertexDic.put(splited[1],vertexIndex);
                vertexIndex++;
            }

            value = callGraph.get(splited[0]);
            if(value==null)
                value = new LinkedHashSet<String>();
            value.add(splited[1]);
            callGraph.put(splited[0],value);
        }
        return vertexIndex;
    }

    private static String removeDollar(String s) {
        int index;
        index = s.indexOf("$");

        if(index!=-1)
            s = s.substring(0,index);
        return s;
    }

    private static String cleanString(String str) {
        String[] result = str.split(":");
        int indexOf2 = result[2].indexOf("(");
        if(indexOf2 == -1) {
            indexOf2 = result[2].indexOf(" ");
            if(indexOf2 == -1) {
                indexOf2 = result[2].length();
            }
        }

        return removeDollar(result[1]) + ":" + result[2].substring(0,indexOf2);
    }



    private static void writeLineToCSV(String lineArray[], FileWriter writer) throws IOException {
        StringBuilder sb = new StringBuilder();
        for (int j = 0; j < lineArray.length; j++) {
            sb.append(lineArray[j]);
            if(j<lineArray.length-1)
                sb.append(",");
        }
        sb.append("\n");
        writer.append(sb.toString());
    }

}